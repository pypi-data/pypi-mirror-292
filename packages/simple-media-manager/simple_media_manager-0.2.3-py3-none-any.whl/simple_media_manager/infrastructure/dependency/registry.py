from simple_media_manager.domain.repository.image import CompoundImageRepository
from simple_media_manager.domain.repository.video import CompoundVideoRepository
from simple_media_manager.infrastructure.adapters.image import DjangoImageReadRepository, DjangoImageWriteRepository
from simple_media_manager.infrastructure.adapters.video import DjangoVideoWriteRepository, DjangoVideoReadRepository

django_compound_image_repository = CompoundImageRepository(read_repository=DjangoImageReadRepository(),
                                                           write_repository=DjangoImageWriteRepository())

django_compound_video_repository = CompoundVideoRepository(read_repository=DjangoVideoReadRepository(),
                                                           write_repository=DjangoVideoWriteRepository())
