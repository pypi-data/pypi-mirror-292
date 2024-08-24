from collections.abc import Iterator
from typing import Any

from django.core.files.uploadedfile import TemporaryUploadedFile

from simple_media_manager.domain.entities.constants import COMPACT_IMAGE_RESIZE_PERCENT, MINIMUM_IMAGE_SIZE, \
    THUMBNAIL_IMAGE_RESIZE_PERCENT
from simple_media_manager.domain.repository.image import ImageReadRepository, ImageWriteRepository
from simple_media_manager.infrastructure.models import Image
from simple_media_manager.infrastructure.services.django import update
from simple_media_manager.infrastructure.services.image import ImageProcessingService


class DjangoImageWriteRepository(ImageWriteRepository):

    def update(self, pk: int, data: dict[str:Any], image_processing_service: ImageProcessingService = ImageProcessingService()):
        instance: Image
        image = Image.objects.get(pk=pk)
        fields = ['name', 'original']
        instance, is_updated = update(instance=image, fields=fields, data=data)
        if not instance.original.file < MINIMUM_IMAGE_SIZE:
            thumbnail = image_processing_service.resize_image(image_file=data['file'],
                                                              resize_percent=THUMBNAIL_IMAGE_RESIZE_PERCENT)
            compact = image_processing_service.resize_image(image_file=data['file'],
                                                            resize_percent=COMPACT_IMAGE_RESIZE_PERCENT)
            instance.thumbnail = thumbnail
            instance.compact = compact
            instance.save()
        else:
            thumbnail = data['file']
            compact = image_processing_service.resize_image(image_file=data['file'],
                                                            resize_percent=COMPACT_IMAGE_RESIZE_PERCENT)
            instance.thumbnail = thumbnail
            instance.compact = compact
            instance.save()
        return instance

    def save(self,
             file: TemporaryUploadedFile,
             name: str = '',
             image_processing_service: ImageProcessingService = ImageProcessingService()) -> Image:
        return Image.objects.create(name=name,
                                    original=file,
                                    thumbnail=image_processing_service.resize_image(image_file=file, resize_percent=60),
                                    compact=image_processing_service.resize_image(image_file=file, resize_percent=80))

    def create(self,
               file: TemporaryUploadedFile,
               name: str,
               image_processing_service: ImageProcessingService = ImageProcessingService()) -> Image:
        """
        Creates a new Image object, and it isn't saved into database, only held in RAM
        """

        if not file.size < MINIMUM_IMAGE_SIZE:
            instance = Image(name=name,
                             original=file,
                             thumbnail=image_processing_service
                             .resize_image(image_file=file,
                                           resize_percent=THUMBNAIL_IMAGE_RESIZE_PERCENT),
                             compact=image_processing_service
                             .resize_image(image_file=file,
                                           resize_percent=COMPACT_IMAGE_RESIZE_PERCENT))
        else:
            instance = Image(name=name,
                             original=file,
                             thumbnail=file,
                             compact=image_processing_service
                             .resize_image(image_file=file,
                                           resize_percent=THUMBNAIL_IMAGE_RESIZE_PERCENT))

        return instance

    def bulk_create(self, files: list) -> list[Image]:
        images = [self.create(file=image, name=image.name) for image in files]
        return images

    def bulk_save(self, files: list) -> Iterator[Image]:
        new_images = self.bulk_create(files=files)
        return Image.objects.bulk_create(new_images)

    def delete(self, pk: int):
        Image.objects.get(id=pk).delete()


class DjangoImageReadRepository(ImageReadRepository):
    def all(self) -> Iterator[Image]:
        return Image.objects.all()

    def get(self, pk: int) -> Image:
        return Image.objects.get(pk=pk)

    def find(self, name: str) -> Iterator[Image]:
        return Image.objects.filter(name__icontains=name)
