
from django.http import HttpResponse
from django.utils.crypto import get_random_string
import logging
from pathlib import Path
import json
import base64

from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.core.cache import cache
from requests import post as req_post
from requests import exceptions
from rest_framework import serializers
from django.http import HttpResponse,  HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login as auth_login
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


from apps.core.ua_sign import decrypt_data
from apps.core.models import CoreOrganization

from .settings import *


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve(strict=True).parent


class BearesSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class UserUAoauthSerializer(serializers.Serializer):
    """{
    "access_token": "2c71170938c539f628b9a187ef776061e5431979",
    "token_type": "bearer",
    "expires_in": 1596225158,
    "refresh_token": "cc4b144cccd033594104ead46f1ab1aaa127787a",
    "user_id": "66666666"
}"""
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    refresh_token = serializers.CharField()
    user_id = serializers.CharField()


@sync_to_async
def get_data(serializer):
    return serializer.data


# TODO Перевести в асинхронний режим


async def get_acess_token(request):
    logger.debug('get_acess_token')
    serializer = BearesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # self.redirect_uri = serializer.validated_data['redirect_uri'],
    data = {"grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": serializer.validated_data['code'],
            # "redirect_uri": self.redirect_uri
            }
    try:
        res = req_post(ACCESS_TOKEN_URL, data=data)
    except exceptions.ConnectionError as e:
        raise ValidationError({
            'non_field_errors': "Не вдалось під'єднатись до серверу авторизації",
            'details': str(e)})
    if res.status_code == 200:
        return res.json()
    elif res.status_code == 401:
        raise ValidationError(res.json())


class UAOauthLoginView(APIView):
    permission_classes = (AllowAny,)
    UserModel = get_user_model()

    def get(self, request, *args, **kwargs):

        try:
            self.request = request
            # отримуємо код
            code_data = self.get_acess_token(request)
            # отримуємо дані аутентифікації
            user_data = self.get_user_data(code_data)
            return self.login(user_data)
        except ValidationError as e:
            message = e.args[0]['non_field_errors']
            logger.error(str(e.args))
            messages.error(request, message)
            # TODO замінити на reverce
            return HttpResponseRedirect('/mrs/login/')
        except Exception as e:
            logging.error(e, exc_info=True)
            messages.error(
                request, 'Сталась помилка при спробі авторизації. Можливо Ви перейшли за прямим посиланням, або вийшов час дії авторизаціної сесії. Спробуйте знову')
            return HttpResponseRedirect('/mrs/login/')

    def get_acess_token(self, request):
        logger.debug('get_acess_token')
        # serializer = BearesSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.redirect_uri = serializer.validated_data['redirect_uri'],
        data = {"grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": request.GET['code'],
                # "redirect_uri": self.redirect_uri
                }
        try:
            res = req_post(ACCESS_TOKEN_URL, data=data)
        except exceptions.ConnectionError as e:
            raise ValidationError({
                'non_field_errors': "Не вдалось під'єднатись до серверу авторизації",
                'details': str(e)})
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            raise ValidationError(
                {'non_field_errors': res.json().get('message')})

    def get_user_data(self, code_data):
        logger.debug('get_user_data')
        serializer = UserUAoauthSerializer(data=code_data)
        serializer.is_valid(raise_exception=True)

        # user_info_fields = "edrpoucode,drfocode,givenname,lastname"
        cert_b64 = None
        # Перевіряємо наявність файлу відкритого ключа
        cert_path = UAAUTH_CERT_FILE_NAME
        if not os.path.exists(cert_path):
            raise Exception('Відсутній файл сертифікату (відкритий ключ)')

        with open(cert_path, 'rb') as cert_f:
            cert_data = cert_f.read()
            cert_b64 = base64.b64encode(cert_data)
            # cache.set(UAAUTH_CERT_FILE_NAME, cert_b64,)

        if not cert_b64:
            raise Exception('Відсутній сертифікат (відкритий ключ)')

        data = {"access_token": serializer.validated_data['access_token'],
                "user_id": serializer.validated_data['user_id'],
                "cert": cert_b64
                }
        res = req_post(USER_INFO_URL, data=data)
        logger.info(USER_INFO_URL+'?='+"access_token=" +
                    serializer.validated_data['access_token']+'&'"user_id=" + serializer.validated_data['user_id'])

        if res.status_code == 200:
            res_json = res.json()
            if res_json.get('error'):
                raise ValidationError(
                    {'non_field_errors': res_json.get('message')})
            # Перевіряємо наявність файлу закритого ключа
            stamp_path = UAAUTH_KEY_FILE_NAME
            if not os.path.exists(stamp_path):
                raise Exception('Відсутній файл ключа')

            decrypted_result = decrypt_data(
                res_json['encryptedUserInfo'].encode(), stamp_path, UAAUTH_ENCRYPTION_KEY_PASS)
            if decrypted_result.get('code') != 0:
                logger.error(decrypted_result)
                raise ValidationError({
                    'non_field_errors': 'Помилка при взаємодії з сервером авторизації'})
            data = json.loads(decrypted_result.get('data'))
            return data
        elif res.status_code == 401:
            raise ValidationError(
                {'non_field_errors': res.json().get('message')})

    def get_user(self, data):
        from apps.audit.models import LoginEvent
        from apps.audit.settings import REMOTE_ADDR_HEADER
        logger.debug('get_user')
        # Отрмуємо користувача з ІПН, якщо існує - повертаємо користувача
        ipn = data.get('drfocode')
        edrpou = data.get('edrpoucode')

        if not edrpou:
            user_q = self.UserModel.objects.filter(ipn=ipn)

            if user_q.exists():
                user = user_q.first()
            else:
                user = self.UserModel.objects.create(ipn=ipn,
                                                     state=data.get('title'),
                                                     username=f'auto_user_{ipn}_{get_random_string(length=4)}',
                                                     first_name=data['givenname'],
                                                     last_name=data['lastname'],
                                                     is_staff=True,
                                                     is_active=True,
                                                     email=data.get('email')
                                                     )
                default_user_group = Group.objects.get(
                    name='Військовозобовязаний')
                user.groups.add(default_user_group)
            return user
        else:
            if CoreOrganization.objects.filter(edrpou=edrpou).exists():
                organization = CoreOrganization.objects.filter(
                    edrpou=edrpou).first()
            else:
                raise ValidationError(
                    {'non_field_errors': f" ЄДРПОУ {edrpou} - НЕ Є ТЦК, або ще не створена. Зверніться до адміністратора"})
            
            authorized_person = organization.authorized_persons.filter(
                code=ipn).first()
            if not authorized_person:
                LoginEvent.objects.create(
                    login_type=LoginEvent.FAILED,
                    username=None,
                    user_as_string=f"РНОКПП:{ipn}; {data.get('lastname')} {data.get('givenname')}",
                    user_id=None,
                    remote_ip=self.request.META[REMOTE_ADDR_HEADER],
                    comment=f"{data['lastname']} {data['givenname']} - не включений до списку уповноважених осіб"
                )
                raise ValidationError(
                    {'non_field_errors': f"{data['lastname']} {data['givenname']} - не включений до списку уповноважених осіб, або не активний"})
            if not authorized_person.active:
                LoginEvent.objects.create(
                    login_type=LoginEvent.FAILED,
                    username=None,
                    user_as_string=f"РНОКПП:{ipn}; {data.get('lastname')} {data.get('givenname')}",
                    user_id=None,
                    remote_ip=self.request.META[REMOTE_ADDR_HEADER],
                    comment=f"{data['lastname']} {data['givenname']} - не активний"
                )
                raise ValidationError(
                    {'non_field_errors': f"{data['lastname']} {data['givenname']} - не включений до списку уповноважених осіб, або не активний"})
            user_q = self.UserModel.objects.filter(ipn=ipn,organization=organization)
            if user_q.exists():
                user = user_q.first()
            else:
                user = self.UserModel.objects.create(ipn=ipn,
                                                     state=data.get('title'),
                                                     username=f'auto_user_{ipn}_{get_random_string(length=4)}',
                                                     first_name=data['givenname'],
                                                     last_name=data['lastname'],
                                                     is_staff=True,
                                                     is_active=True,
                                                     organization=organization,
                                                     email=data.get('email')
                                                     )
                default_user_group = Group.objects.get(name='ТЦК СП')
                user.groups.add(default_user_group)
            return user

    def get_response(self):
        response = Response(self.token_serializer.data,
                            status=status.HTTP_200_OK)
        return response

    def login(self, data):
        logger.info('login')
        logger.info(data)
        self.user = self.get_user(data)
        logger.info(f'user:{self.user}')
        auth_login(self.request, self.user)
        redirect = self.request.GET.get('next', '/')
        return HttpResponseRedirect(redirect)
