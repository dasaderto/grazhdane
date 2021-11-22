import os
import uuid
from abc import ABC
from typing import IO, Optional

import aiofiles
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from grazhdane import config


class BaseService(ABC):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db


class FileFormatService:
    VIDEO_FORMAT = "video"
    IMAGE_FORMAT = "image"
    ICON_FORMAT = "icon"
    DOCUMENT_FORMAT = "document"
    AUDIO_FORMAT = "audio"

    FORMATS = {
        VIDEO_FORMAT: ['m4v', 'mp4', 'mov'],
        IMAGE_FORMAT: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'wav', 'bmp'],
        ICON_FORMAT: ['svg'],
        DOCUMENT_FORMAT: ['doc', 'docx', 'xlsx', 'xls', 'pdf'],
        AUDIO_FORMAT: ['mp3', 'cdr', 'mpga'],
    }

    def is_video(self, file_format: str):
        return file_format in self.FORMATS[self.VIDEO_FORMAT] or file_format == self.VIDEO_FORMAT

    def get_file_type(self, file_format: str) -> Optional[str]:
        file_format = file_format.lower()
        for fmt, extensions in self.FORMATS.items():
            if file_format in extensions:
                return fmt

        return None


class AttachmentStorage:
    _file_type = None

    def __init__(self, file: IO, filename: str, dir_name: str):
        self.file = file
        self._filename = filename
        self.dir_name = dir_name

    @property
    def file_type(self) -> str:
        if not self._file_type:
            split_filename = self._filename.split(".")
            ext = split_filename[-1]
            self._file_type = FileFormatService().get_file_type(file_format=ext)
        return self._file_type

    @property
    def filename(self) -> str:
        split_filename = self._filename.split(".")
        ext = split_filename[-1]
        self._file_type = FileFormatService().get_file_type(file_format=ext)
        new_filename = slugify(f"{str(uuid.uuid4())}_{self._filename.replace(ext, '')}") + f".{ext}"
        return new_filename

    async def store(self):
        filename = self.filename
        async with aiofiles.open(os.path.join(config.STORAGE_ROOT, self.dir_name, filename), mode='wb') as f:
            await f.write(self.file.read())

        return os.path.join(config.STORAGE_URL, self.dir_name, filename)
