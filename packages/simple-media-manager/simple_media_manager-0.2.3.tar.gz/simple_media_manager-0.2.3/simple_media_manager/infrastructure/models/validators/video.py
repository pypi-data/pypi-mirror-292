from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_video_extension(value):
    white_list = ['mkv', 'mp4', 'avi', 'webm', 'flv', 'vob', 'gif', 'm4v']
    filename = value.name
    ext = filename.split('.')[-1]
    ext = ext.lower()
    if ext not in white_list:
        raise ValidationError(str(_('Type is not valid ,valid types are')) + '  '.join(white_list))
