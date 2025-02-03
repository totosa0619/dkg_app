import uuid

from django.contrib.auth import get_user_model
from django.db import models

from core.storage import AzureStaticStorage
from storage import blob


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='profile', on_delete=models.CASCADE)
    is_editor = models.BooleanField(default=False)


class UserFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    source = models.FileField(upload_to='files/', storage=AzureStaticStorage)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.source.name

    def to_dict(self):
        user = self.user.id if self.user is not None else ''
        return {
            "filename": self.source.name,
            "url": blob.get_path(self.source.name),
            "id": self.id,
            "user_id": user,
        }
