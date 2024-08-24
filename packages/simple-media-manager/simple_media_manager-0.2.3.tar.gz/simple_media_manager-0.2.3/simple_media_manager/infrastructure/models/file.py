from django.db import models
from django.utils import timezone


class File(models.Model):
    name = models.CharField(null=True, max_length=100)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
