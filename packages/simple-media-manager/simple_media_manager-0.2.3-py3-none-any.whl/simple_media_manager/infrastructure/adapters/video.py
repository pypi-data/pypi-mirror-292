from typing import Iterator

from simple_media_manager.domain.repository.video import VideoWriteRepository, VideoReadRepository
from simple_media_manager.infrastructure.models import Video


class DjangoVideoReadRepository(VideoReadRepository):

    def get(self, pk: int):
        pass

    def find(self, name: str):
        pass

    def all(self):
        pass


class DjangoVideoWriteRepository(VideoWriteRepository):
    def save(self, file: bytes, name: str):
        pass

    def create(self, file: bytes, name: str) -> Video:
        instance = Video(file=file, name=name)
        return instance

    def bulk_create(self, files: list) -> list[Video]:
        videos = [self.create(file=video, name=video.name) for video in files]
        return videos

    def bulk_save(self, files: list) -> Iterator[Video]:
        new_videos = self.bulk_create(files=files)
        return Video.objects.bulk_create(new_videos)

    def delete(self, pk: int):
        pass
