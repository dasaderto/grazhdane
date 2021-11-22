from dataclasses import dataclass
from typing import IO


@dataclass
class UploadedFileType:
    filename: str
    file: IO
