from simple_media_manager.domain.command import Command
from simple_media_manager.domain.repository.video import VideoRepository


class BaseVideoCommand(Command):
    def __init__(self, repository: VideoRepository):
        self.repository = repository


class BulkUploadVideoCommand(BaseVideoCommand):
    def handle(self, files: list[dict]):
        return self.repository.bulk_save(files=files)
