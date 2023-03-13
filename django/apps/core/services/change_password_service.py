from rest_framework.exceptions import APIException,ParseError,PermissionDenied
from django.contrib.auth import get_user_model

CoreUser = get_user_model()


class ChangePassword:
    def __init__(self, request, data):
        self.request = request
        self.data = data

    def run(self):
        password = self.validate_password()
        self.check_user()
        self.change_password(password)
        return self.user

    def validate_password(self):
        # Check that the two password entries match
        password = self.data.get("password")
        password_confirm = self.data.get("password_confirm")
        if password != password_confirm:
            raise ParseError({"password_confirm":"Паролі не співпадають"})
        return password_confirm

    def check_administrator(self):
        pass

    def check_user(self):
        """Перевірити кристувача. Якщо запит на зміну пароля відіслав суперюзер- дозволяємо заміну.
        Якщо запит надіслав інший користувач - перевіряємо чи він з тої ж організації що і користувач, пароль якого змінюється."""
        self.user = self.data.get("user")
        admin_user = self.request.user
        if admin_user.is_superuser:
            return
        ##Перевіряємо чи співпапдає організація
        if self.user.organization != admin_user.organization:
            raise PermissionDenied('Ви не можете змінити пароль користувача іншої організації.')
        ##Перевіряємо чи має користувач права на заміну пароля
        if not admin_user.has_perm('core.change_local_user_password'):
            raise PermissionDenied('У Вас не достатньо прав на зміни пароля користувача')


    def change_password(self, password):
        # Save the provided password in hashed format
        self.user.set_password(password)
        self.user.save()
