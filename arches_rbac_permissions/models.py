import uuid
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField, deletion
from arches.app.models.models import ResourceInstance
from arches.app.utils.module_importer import get_class_from_modulename
from arches_rbac_permissions.const import RBACExtensionType

class SavedSearch(models.Model):
    savedsearchid = models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)
    user = models.ForeignKey(User, db_column="user_id", on_delete=deletion.CASCADE)
    name = models.TextField()
    query = JSONField()
    created = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(SavedSearch, self).__init__(*args, **kwargs)
        if not self.savedsearchid:
            self.savedsearchid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "saved_searches"

class InclusionRule(models.Model):
    inclusionruleid = models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)
    owner = models.ForeignKey(User, db_column="owner_id", on_delete=deletion.SET_NULL, null=True)
    name = models.TextField()
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    definition = JSONField()
    created = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(InclusionRule, self).__init__(*args, **kwargs)
        if not self.inclusionruleid:
            self.inclusionruleid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "inclusion_rules"

    def get_class_module(self):
        return get_class_from_modulename(
            self.modulename, self.classname, RBACExtensionType.RULES
        )

    def get_search_rule_url(self):
        return self.get_class_module().do_get_search_rule_url(self)
