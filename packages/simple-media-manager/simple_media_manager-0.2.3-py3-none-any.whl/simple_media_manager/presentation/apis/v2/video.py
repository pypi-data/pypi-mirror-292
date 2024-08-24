from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from simple_media_manager.domain.command.video import BulkUploadVideoCommand
from simple_media_manager.infrastructure.common.class_responses.error_response import ErrorResponse
from simple_media_manager.infrastructure.dependency.registry import \
    django_compound_video_repository as DjangoCompoundVideoRepository
from simple_media_manager.presentation.apis.v2.serializers.video import BriefVideoOutputSerializer, VideoMultipleInputSerializer


class UploadVideosApi(APIView):

    def __init__(self, **kwargs):
        super(UploadVideosApi, self).__init__(**kwargs)
        self.command = BulkUploadVideoCommand(repository=DjangoCompoundVideoRepository)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "videos": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "binary", }}}}},
        responses=BriefVideoOutputSerializer
    )
    def post(self, request):
        serializer = VideoMultipleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.command.handle(files=serializer.validated_data.get('videos'))
            response = BriefVideoOutputSerializer(instance, many=True, context={'request': request}).data
            return Response(response)
        except Exception as exception:
            return ErrorResponse(exception=exception)
