from rest_framework import serializers

from simple_media_manager.infrastructure.common.serializers.custom_fields.fields import Base64ImageField
from simple_media_manager.infrastructure.models import Image


class ImageInputSerializer(serializers.Serializer):
    image = Base64ImageField(required=False, allow_null=False, allow_empty_file=False)
    name = serializers.CharField(required=False, allow_null=False)
    categories = serializers.ListField(required=True, allow_null=False, child=serializers.IntegerField())


class ImageMultipleInputSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(required=True, use_url=False))


class ImageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class BriefImageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'thumbnail')


class BriefImageOutputSerializerTypeTwo(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'thumbnail', 'compact')


class BriefImageOutputSerializerTypeThree(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'thumbnail',)


class SearchImageInputParameterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=False)
