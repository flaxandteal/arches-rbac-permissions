import logging
from django.db import transaction
from django.contrib.auth.models import User, Permission, Group as DjangoGroup
from arches.app.models.system_settings import settings, SystemSettings
from arches.app.permissions.arches_permission_base import get_nodegroups_by_perm_for_user_or_group, ObjectPermissionChecker
from arches.app.models.models import Node, MapLayer, Graph, GraphModel, ResourceInstance, Resource, NodeGroup
from arches_orm import arches_django as _
from arches_orm.models import Person, Set, LogicalSet, Group
from arches_orm.view_models import ResourceInstanceViewModel
from arches_orm.arches_django.datatypes.django_group import MissingDjangoGroupViewModel
from arches_orm.adapter import context_free
from arches_querysets.models import ResourceTileTree
from arches_rbac_permissions.service import trigger

logger = logging.getLogger(__name__)

class NoSubjectError(RuntimeError):
    pass

class CasbinDB:
    def __init__(self, graph_remappings):
        self.graph_remappings = graph_remappings
        self.Group = Group
        self.Set = Set
        self.Person = Person
        self.LogicalSet = LogicalSet
        self.ResourceInstanceViewModel = ResourceInstanceViewModel

    @staticmethod
    @context_free
    def _ri_to_django_groups(group: Group):
        if not group.django_group:
            django_group, _ = DjangoGroup.objects.get_or_create(name=str(group))
            group.django_group = [django_group]
            group.save()
        return group.django_group

    @staticmethod
    @context_free
    def _django_group_to_ri(django_group: DjangoGroup):
        # TODO: a more robust mapping
        group = Group.where(name=django_group.name).get()
        if not group:
            group = Group.create()
            basic_info = group.basic_info.append()
            basic_info.name = django_group.name
            group.save()
        else:
            group = group[0]
        return group

    @property
    def _enforcer(self):
        from dauthz.core import enforcer
        return enforcer

    @context_free
    def recalculate_table(self):
        with transaction.atomic():
            self._recalculate_table_real()

    def _recalculate_table_real(self):
        print("RECALC", 1)
        groups = settings.GROUPINGS["groups"]
        # TODO - going to need help rewriting this for QuerySets
        root_group = Group.find(groups["root_group"])
        self._enforcer.clear_policy()

        # We bank permissions for all Django groups for nodegroups,
        # (implicitly resource models) and map layers, but nothing else.
        print("RECALC", 2)
        for django_group in DjangoGroup.objects.all():
            print(django_group.name)
            group_key = self._subj_to_str(django_group)
            self._enforcer.add_named_grouping_policy("g", group_key, f"dgn:{django_group.name}")
            # The default permissions are (still) all perms, if the nodegroup perms set is empty
            nodegroups = {
                str(nodegroup.pk): set(perms) if perms else set(self.graph_remappings.values())
                for nodegroup, perms in
                get_nodegroups_by_perm_for_user_or_group(django_group, ignore_perms=True).items()
            }
            print("RECALC", 2, 1)
            print("RECALC", 2, 2)
            nodes = Node.objects.filter(nodegroup__in=nodegroups).select_related("graph").only("graph__graphid", "nodegroup_id")
            print("RECALC", 2, 3)
            graphs = {}
            graph_perms = {}
            for node in nodes:
                key = f"gp:{node.graph.graphid}"
                graph_perms.setdefault(key, set())
                graph_perms[key] |= set(nodegroups[str(node.nodegroup_id)])
                graphs[key] = node.graph
            print("RECALC", 2, 4)
            for graph, perms in graph_perms.items():
                if graphs[graph].isresource and str(graph[3:]) != SystemSettings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                    for perm in perms:
                        self._enforcer.add_policy(group_key, graph, str(perm))
            print("RECALC", 2, 5)
            map_layer_perms = ObjectPermissionChecker(django_group)
            for map_layer in MapLayer.objects.all():
                perms = set(map_layer_perms.get_perms(map_layer))
                map_layer_key = self._obj_to_str(map_layer)
                for perm in perms:
                    self._enforcer.add_policy(group_key, map_layer_key, str(perm))
            print("RECALC", 2, 6)
        print("RECALC", 3)

        groups_seen = dict()
        sets = []
        def _fill_group(group, ancestors):
            group_key = self._subj_to_str(group)
            if group_key in ancestors:
                try:
                    group_name = str(group)
                except Exception as e:
                    group_name = "(name error)"
                    logging.exception("Name to string casting for a group: %s", str(e))
                logging.warn("There is a circular reference - %s for %s", group_key, group_name)
                return []
            if group_key in groups_seen:
                return groups_seen[group_key]
            users = []
            print(" " * len(ancestors), len(group.members), "members in", group.basic_info[0].name)
            for n, member in enumerate(group.members):
                if isinstance(member, Group):
                    member_key = self._subj_to_str(member)
                    print(" " * (1 + len(ancestors)), n, "/", len(group.members), member_key)
                    # This is the reverse of what might be expected, as the more deeply
                    # nested a group is, the _fewer_ permissions it has. Conversely, the
                    # top groups gather all the permissions from the groups below them,
                    # which fits Casbin's transitivity when top groups are _Casbin members of_
                    # the groups below them.
                    self._enforcer.add_named_grouping_policy("g", group_key, member_key)
                    ancestors = list(ancestors)
                    ancestors.append(group_key)
                    users += _fill_group(member, ancestors)
                elif member.user_account:
                    member_key = self._subj_to_str(member)
                    self._enforcer.add_role_for_user(member_key, group_key)
                    users.append(member.user_account)
                else:
                    logger.warn("A membership rule was not added as no User was attached %s", member.id)
            # This is a workaround for now, to avoid losing nodegroup restriction entirely.
            # The (RI) Group names will be matched to Django groups, and those used to build the nodegroup
            # permissions.
            # for django_group in self._ri_to_django_groups(group):
            #     nodegroups = get_nodegroups_by_perm_for_user_or_group(django_group, ignore_perms=True)
            #     for nodegroup, perms in nodegroups.items():
            #         for act in perms:
            #             obj_key = self._obj_to_str(nodegroup)
            #             self._enforcer.add_policy(group_key, obj_key, str(act))
            # TODO: Removing for now
            # try:
            #     arches_plugins = group.arches_plugins
            #     print(arches_plugins, "Arches Plugins #1")
            #     for arches_plugin in arches_plugins:
            #         if not isinstance(arches_plugin, ArchesPlugin):
            #             try:
            #                 logger.warn("A non-plugin resource was listed as an Arches plugin in a group: %s in %s", arches_plugin.id, group.id)
            #             except Exception as exc:
            #                 logger.warn("A non-plugin resource was listed as an Arches plugin in a group: %s", str(exc))
            #             continue
            #         print(arches_plugin, "Arches Plugins #2")
            #         try:
            #             identifier = uuid.UUID(arches_plugin.plugin_identifier)
            #             plugin = Plugin.objects.get(pk=identifier)
            #         except ValueError:
            #             plugin = Plugin.objects.get(slug=arches_plugin.plugin_identifier)
            #         for obj_key in (f"pl:{key}" for key in (plugin.pk, plugin.slug) if key):
            #             self._enforcer.add_policy(group_key, obj_key, "view_plugin")
            #             print("Arches Plugins #3", group_key, obj_key)
            # except Exception as exc:
            #     print("Could not get Arches Plugins", exc)
            for permission in group.permissions:
                if not permission.action:
                    logging.warn("Permission action is missing: %s: %s on %s", group_key, str(permission.action), str(permission.object))
                    continue
                for act in permission.action:
                    if not permission.object:
                        logging.warn("Permission object is missing: %s %s", group_key, str(permission.object))
                        continue
                    for obj in permission.object:
                        obj_key = self._obj_to_str(obj)
                        if obj_key.startswith("g2"):
                            sets.append(obj_key)
                        self._enforcer.add_policy(group_key, obj_key, str(act.conceptid))
            if len(group.django_group) == 0:
                self._ri_to_django_groups(group)

            # TODO: come back to
            # for gp in group.django_group:
            #     if not gp or gp.pk is None or isinstance(gp, MissingDjangoGroupViewModel):
            #         logging.warn("Missing Django Group in a group: %s for %s", group_key, str(gp.pk) if gp else str(gp))
            #         continue
            #     if list(gp.user_set.all()) != users:
            #         print(users)
            #         gp.user_set.set(users)
            #         gp.save()
            groups_seen[group_key] = users
            return users

        sets = []

        print("RECALC", 4)
        _fill_group(root_group, list())
        print("RECALC", 5)

        for user in User.objects.all():
            user_key = self._subj_to_str(user)
            for group in user.groups.all():
                group_key = self._subj_to_str(group)
                self._enforcer.add_named_grouping_policy("g", user_key, group_key)
        print("RECALC", 6)

        def _fill_set(st, ancestors):
            set_key = self._obj_to_str(st)
            if set_key in ancestors:
                try:
                    set_name = str(st)
                except Exception as e:
                    set_name = "(name error)"
                    logging.exception("Name to string casting for a set: %s", str(e))
                logging.warn("There is a circular nested set reference - %s for %s", set_key, set_name)
                return
            if set_key in sets:
                sets.remove(set_key)
            # We do not currently handle nesting of logical sets
            if isinstance(st, Set):
                if st.nested_sets:
                    for nst in st.nested_sets:
                        nested_set_key = self._obj_to_str(nst)
                        self._enforcer.add_named_grouping_policy("g2", nested_set_key, set_key)
                        ancestors = list(ancestors)
                        ancestors.append(set_key)
                        _fill_set(nst, ancestors)
                if st.members:
                    for member in st.members:
                        member_key = self._obj_to_str(member)
                        self._enforcer.add_named_grouping_policy("g2", member_key, set_key)

        while sets:
            obj_key = sets[0]
            if obj_key.startswith("g2l:"):
                root_set = LogicalSet.find(obj_key.split(":")[1])
            else:
                root_set = Set.find(obj_key.split(":")[1])
            _fill_set(root_set, [])
        print("RECALC", 7)

        self._enforcer.save_policy()
        self._enforcer.load_policy()
        print("RECALC", 8)


    @context_free
    def _subj_to_str(self, subj):
        if isinstance(subj, DjangoGroup):
            subj = f"dg:{subj.pk}"
        if isinstance(subj, Person):
            if not subj.user_account:
                raise NoSubjectError(subj)
            subj = f"u:{subj.user_account.pk}"
        if isinstance(subj, User):
            subj = f"u:{subj.pk}"
        elif isinstance(subj, Group):
            subj = f"g1:{subj.id}"
        elif isinstance(subj, str) and ":" in subj:
            return subj
        else:
            raise ArchesNotUserNorGroup(str(subj))
        return subj

    @context_free
    def _obj_to_str(self, obj):
        if obj is None:
            raise NotImplementedError()
        elif isinstance(obj, str) and ":" in obj:
            return obj
        elif isinstance(obj, Set):
            obj = f"g2:{obj.id}"
        elif isinstance(obj, LogicalSet):
            obj = f"g2l:{obj.id}"
        elif isinstance(obj, Graph) or isinstance(obj, GraphModel):
            obj = f"gp:{obj.pk}"
        # TODO: leave out of Application for now
        # elif isinstance(obj, ArchesPlugin): # Removing for now
        #     obj = f"pl:{obj.plugin_identifier}"
        # elif isinstance(obj, Plugin):
        #    obj = f"pl:{obj.pk}"
        elif isinstance(obj, ResourceInstanceViewModel):
            obj = f"ri:{obj.id}"
        elif isinstance(obj, ResourceInstance) or isinstance(obj, Resource):
            obj = f"ri:{obj.pk}"
        elif isinstance(obj, NodeGroup):
            obj = f"ng:{obj.pk}"
        elif isinstance(obj, MapLayer):
            obj = f"ml:{obj.pk}"
        elif isinstance(obj, Permission):
            obj = f"ct:{obj.content_type}"
        else:
            obj = f"o:{obj.pk}"
        return obj
