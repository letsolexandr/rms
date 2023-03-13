import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SIGN_FILE_NAME = os.path.join(BASE_DIR, 'sign',os.environ.get("SIGN_KEY","Da.tat"))
SIGN_PWD = os.environ.get("SIGN_PWD")
