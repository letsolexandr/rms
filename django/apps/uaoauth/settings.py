import os
from pathlib import Path
from django.conf import settings


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


CLIENT_ID = settings.UA_OAUTH_CLIENT_ID
CLIENT_SECRET = settings.UA_OAUTH_CLIENT_SECRET


ACCESS_TOKEN_URL = settings.UA_OAUTH_ACCESS_TOKEN_URL
USER_INFO_URL = settings.UA_OAUTH_USER_INFO_URL

UAAUTH_ENCRYPTION_KEY_PASS = os.environ.get("SIGN_PWD")
 
UAAUTH_KEY_FILE_NAME = os.path.join(BASE_DIR, 'sign',os.environ.get("SIGN_KEY","dat.dat"))
UAAUTH_CERT_FILE_NAME = os.path.join(BASE_DIR, 'sign',os.environ.get("SIGN_CERT","dat.crt"))

UAAUTH_CERT_CACHE_TIME =  60*60*12##12 годин
