from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE
from rest_framework.views import exception_handler


class ServiceException(APIException):
    status_code = 409
    default_detail = ''
    # default_code = 'service_unavailable'


class AuthorNotSet(Exception):
    def __init__(self, *args):
        default_message = 'Автор запису не вказаний'
        if not args: args = (default_message,)
        super().__init__(*args)


class AuthorOrganizationNotSet(Exception):
    def __init__(self, *args):
        default_message = 'Не вказана організація автора даних. Вкажіть організацю для автора в моделі користувача'
        if not args: args = (default_message,)
        super().__init__(*args)



class DeleteProtectedFieldException(APIException):
    status_code = 403
    def __init__(self, *args):
        default_message = 'Спроба видалити захищений обєкт'
        if not args: args = (default_message,)
        super().__init__(*args)


class ChangeProtectedFieldException(APIException):
    status_code = 403
    def __init__(self, *args):
        default_message = 'Спроба змінити захищене від зміни поле моделі'
        if not args: args = (default_message,)
        super().__init__(*args)


class ToLargeFileException(APIException):
    status_code = HTTP_413_REQUEST_ENTITY_TOO_LARGE
    def __init__(self, *args):
        default_message = 'Розмір файлу, який Ви намагаєтесь завантажити перевищує встановлений ліміт'
        if not args: args = (default_message,)
        super().__init__(*args)
