import os
from pathlib import Path

LOGS_DIR = Path(os.getenv("LOGS_DIR", "./data/logs"))
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "./data/media"))
SECRET_KEY_PATH = Path(os.getenv("SECRET_KEY_PATH", "./data/secret.key"))