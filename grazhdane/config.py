import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
STORAGE_ROOT = os.path.join(MEDIA_ROOT, "storage")
STORAGE_URL = "/media/storage/"
