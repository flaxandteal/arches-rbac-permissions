import uuid
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField, deletion

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
