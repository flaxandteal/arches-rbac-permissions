from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from casbin_adapter import apps

from .service import trigger


class ArchesSemanticRolesConfig(AppConfig):
    name = "arches_semantic_roles"
    is_arches_application = True

    def ready(self):
        # TODO: This seems to be a new issue on upgrade to Arches 8, but DjangoCasbin should
        # not be using a connection on its ready handler anyway. In practice, it will run
        # initialize_enforcer if is has not been when it needs it.
        apps.CasbinAdapterConfig.ready = lambda _: None
        print("Casbin trigger")
        trigger.initialize()
