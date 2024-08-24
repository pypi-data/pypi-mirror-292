from simple_media_manager.infrastructure.models import File
from django.db import models

from simple_media_manager.infrastructure.models.validators.video import validate_video_extension


class Video(File):
    file = models.FileField(upload_to='media/videos', null=True, validators=[validate_video_extension, ])

    class Meta:
        ordering = ('-created_at',)
