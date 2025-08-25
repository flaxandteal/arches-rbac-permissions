import logging
from django.db import transaction
from django.contrib.auth.models import User, Permission, Group as DjangoGroup
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings, SystemSettings
from arches.app.permissions.arches_permission_base import get_nodegroups_by_perm_for_user_or_group, ObjectPermissionChecker
from arches.app.models.models import Node, MapLayer, Graph, GraphModel, ResourceInstance, Resource, NodeGroup
from arches_orm import arches_django as _
from arches_orm.models import Person, Set, LogicalSet, Group
from arches_orm.view_models import ResourceInstanceViewModel
from arches_orm.adapter import context_free

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

            # This becomes circular if we trigger a resource save
            tile = Tile()
            tile.resourceinstance_id = group.id
            node = group.django_group._parent_pseudo_node.node
            tile.nodegroup_id = node.nodegroup_id
            tile.data = {
                str(node.nodeid): {
                    "groupId": django_group.pk
                }
            }
            tile.save()
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
