from rest_framework.exceptions import APIException,ParseError
from apps.core.models import CoreOrganization
from django.contrib.auth import get_user_model

CoreUser = get_user_model()


class AddUserToOrg:
    def __init__(self, request, data):
        self.request = request
        self.data = data

    def set_organization(self):
        """
        Встановлює організацю для новогоствореного користувача, якщо створює суперюзер -організацюя отримується з даних переданих з клієгнта
        якщо створюється звичайним користувачем, організація витягується з даних автора.
        """
        if self.request.user.is_superuser:
            self.org = self.data.get("organization")
        else:
            self.org = self.request.user.organization

    def run(self):
        self.set_organization()
        password = self.validate_password()
        self.check_user()
        user = self.create_user(password)
        return user

    def validate_password(self):
        # Check that the two password entries match
        password = self.data.get("password")
        password_confirm = self.data.get("password_confirm")
        if password != password_confirm:
            raise ParseError({"password_confirm":"Паролі не співпадають"})
        return password_confirm

    def check_user(self):
        if CoreUser.objects.filter(username=self.data.get('username')).exists():
            raise ParseError({"username":"Користувач з таким логіном вже існує"})

    def create_user(self, password):
        user = CoreUser(
            username=self.data.get('username'),
            first_name=self.data.get('first_name'),
            last_name=self.data.get('last_name'),
            email=self.data.get('email'),
            department=self.data.get('department'),
            organization=self.org,
        )
        user.set_password(password)
        user.save()
        if self.data.get('groups'):
            user.groups.add(*self.data.get('groups'))
            user.save()
        return user
