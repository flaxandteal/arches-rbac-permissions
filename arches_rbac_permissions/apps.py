from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from casbin_adapter import apps


class ArchesRBACPermissionsConfig(AppConfig):
    name = "arches_rbac_permissions"
    is_arches_application = True

    def ready(self):
        # TODO: This seems to be a new issue with Arches 8, but DjangoCasbin should
        # not be using a connection on its ready handler anyway
        apps.CasbinAdapterConfig.ready = lambda _: None
        post_migrate.connect(self.db_ready, sender=self)

    def db_ready(self, **kwargs):
        from casbin_adapter.enforcer import initialize_enforcer

        db_alias = getattr(settings, "CASBIN_DB_ALIAS", "default")
        initialize_enforcer(db_alias)
