import os

from django.core.checks import register, Warning
from django.core.checks import Tags as DjangoTags


@register(DjangoTags.compatibility)
def check_LD_LIBRARY_PATH(app_configs=None, **kwargs):
    ""
    LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH')
    UAAUTH_ENCRYPTION_KEY_PASS = os.environ.get("SIGN_PWD")
    UAAUTH_KEY_FILE_NAME = os.environ.get("SIGN_KEY","dat.dat")
    UAAUTH_CERT_FILE_NAME =os.environ.get("SIGN_CERT","dat.crt")
    # print('UAAUTH_ENCRYPTION_KEY_PASS',UAAUTH_ENCRYPTION_KEY_PASS)
    # print('UAAUTH_KEY_FILE_NAME',UAAUTH_KEY_FILE_NAME)
    # print('UAAUTH_CERT_FILE_NAME',UAAUTH_CERT_FILE_NAME)


    errors = []

    if not LD_LIBRARY_PATH:
        errors.append(
            Warning(
                """Не становлення глобальна змінна LD_LIBRARY_PATH. Неможливо перевірити КЕП""",
                hint=("встановіть змінну середовища 'export LD_LIBRARY_PATH=\"/path/to/module\"'"),
                id='core.ua_sign.W001',
            )
        )
    return errors
