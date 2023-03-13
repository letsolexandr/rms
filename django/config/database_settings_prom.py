import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME','mrs'),
        'USER': os.environ.get('DB_USER','db_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD','db_user'),
        'HOST': os.environ.get('DB_HOST','localhost'),
        'PORT': os.environ.get('DB_PORT','5432')
    },
    'logs': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_LOGS_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT')
    }
}