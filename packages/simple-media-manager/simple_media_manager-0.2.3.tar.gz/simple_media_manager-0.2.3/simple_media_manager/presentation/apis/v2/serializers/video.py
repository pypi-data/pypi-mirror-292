from rest_framework import serializers

from simple_media_manager.infrastructure.models import Video


class VideoMultipleInputSerializer(serializers.Serializer):
    videos = serializers.ListField(child=serializers.FileField(required=True, use_url=False))


class BriefVideoOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'file')
