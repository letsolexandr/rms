import imp
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from django.db.models import ProtectedError
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from ..exceptions import ServiceException
import json
from collections import OrderedDict

from django.core.exceptions import FieldError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import status
from rest_framework.response import Response
from ..exceptions import ChangeProtectedFieldException

from django.conf import settings

DEFAULT_CORE_OPTIONS_CACHE_TIME = 60 * 10  # 10 min

CORE_OPTIONS_CACHE_TIME = getattr(
    settings, 'CORE_OPTIONS_CACHE_TIME', DEFAULT_CORE_OPTIONS_CACHE_TIME)


class CachedOptionsMixin(object):
    @method_decorator(cache_page(CORE_OPTIONS_CACHE_TIME))
    def options(self, request, *args, **kwargs):
        return super(CachedOptionsMixin, self).options(request, *args, **kwargs)


def parse_client_headers(headers):
    od = OrderedDict()
    for header in json.loads(headers):
        value = header.get('value')
        text = header.get('text')
        od[value] = text
    titles = [value for key, value in od.items()]
    return titles
class UserViewMixing(object):
    """Додає автора та редактора при збереженні"""

    def perform_create(self, serializer):
        if self.request.user:
            try:
                serializer.save(author=self.request.user)
            except Exception as e:
                raise e

    def perform_update(self, serializer):
        if self.request.user:
            try:
                serializer.save(editor=self.request.user)
            except Exception as e:
                raise e

    def perform_destroy(self, instance):
        if self.request.user:
            try:
                instance.editor = self.request.user
            except Exception as e:
                raise e
        instance.delete()


class OrganizationFilterMixing:
    def get_queryset(self):
        organization__id = self.request.user.organization_id
        q = super(OrganizationFilterMixing, self).get_queryset()
        try:
            filtered_q = q.filter(organization__id=organization__id)
        except FieldError:
            filtered_q = q
        except Exception as e:
            raise e
        return filtered_q


def dump(obj):
    res = {}
    for attr in dir(obj):
        res[attr] = getattr(obj, attr)
    return res


class DifferentSerializerMixin():
    """Для підтримки різних серіалізаторів даних для різних 'методів'
    наприклад 
    serializer_classes={
        'list':ListSerializerClass,
    }
    """
    serializer_classes = {}

    def get_serializer_class(self):
        if not hasattr(self, 'serializer_classes'):
            return self.serializer_class
        assert isinstance(self.serializer_classes, dict), type(
            self.serializer_classes)
        return self.serializer_classes.get(self.action, self.serializer_class)


class BaseViewSetMixing(UserViewMixing, DifferentSerializerMixin, FlexFieldsModelViewSet):
    http_method_names = ['get', 'delete', 'options', 'patch', 'post']

    def list(self, request, *args, **kwargs):
        
        if self.request.query_params.get('count_only'):
            queryset = self.filter_queryset(self.get_queryset())
            return Response(OrderedDict([
                ('count', queryset.count())
            ]))
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mode = request.GET.get('mode')
        try:
            self.perform_destroy(instance, mode)
        except ProtectedError as e:
            raise ServiceException(
                detail="Неможливо видалити обєкт, на який посилаються інші об'єкти")
        except Exception as e:
            raise e

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, mode=None):
        if self.request.user:
            try:
                instance.editor = self.request.user
            except Exception as e:
                raise e
        instance.delete(mode=mode)

    @swagger_auto_schema(method='get')
    @action(detail=True, methods=['get'])
    def get_deleting_related_objects(self, request, pk=None):
        """Повертає список повязаних обєктів. Обмежений 20 записами. 
        Використовується для попередження користувача про існування звязків перед видаленням обєктів"""
        obj = self.get_object()
        # from django.db import models, router
        # from django.contrib.admin.utils import NestedObjects
        # objs=[obj]
        # try:
        #     obj = objs[0]
        # except IndexError:
        #     return [], {}, set(), []
        # else:
        #     using = router.db_for_write(obj._meta.model)
        # collector = NestedObjects(using=using)
        # collector.collect(objs)
        # perms_needed = set()
        # def format_callback(obj):
        #     return obj

        # to_delete = collector.nested(format_callback)

        # protected = [format_callback(obj) for obj in collector.protected]
        # model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}

        # raise Exception
        # return to_delete, model_count, perms_needed, protected

        related_objects = {"related_objects": [],
                           "count": 0, "title": str(obj)}
        # Перевіряємо чи обєкт захищений від видалення
        obj.check_delete_protected()

        model = ContentType.objects.get_for_model(obj)
        app_label = model.app_label
        model_name = model.model
        perm = f'{app_label}.delete_{model_name}'
        if not request.user.has_perm(perm):
            raise PermissionDenied
        if hasattr(obj, 'get_related_objects_with_count'):
            related_objects = obj.get_related_objects_with_count()
        return Response(related_objects)


class ProtectedMixin(BaseViewSetMixing):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mode = request.GET.get('mode')
        try:
            self.perform_destroy(instance, mode)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChangeProtectedFieldException:
            return Response(status=status.HTTP_403_FORBIDDEN)
        except ProtectedError as e:
            raise ServiceException(
                detail="Неможливо видалити обєкт, на який посилаються інші об'єкти")
        except Exception as e:
            raise e


class BaseOrganizationViewSetMixing(OrganizationFilterMixing, ProtectedMixin):
    def partial_update(self, request, *args, **kwargs):
        # Перевіряємо блокування обєкта
        instance = self.get_object()
        if hasattr(instance, 'blocked_by'):
            if instance.blocked_by and instance.blocked_by != request.user:
                raise ServiceException(
                    f'Неможливо змінити. Обєкт заблокований "{instance.blocked_by.short_name}"')
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Перевіряємо блокування обєкта
        instance = self.get_object()
        if hasattr(instance, 'blocked_by'):
            if instance.blocked_by and instance.blocked_by != request.user:
                raise ServiceException(
                    f'Неможливо змінити. Обєкт заблокований "{instance.blocked_by.short_name}"')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Перевіряємо блокування обєкта
        instance = self.get_object()
        if hasattr(instance, 'blocked_by'):
            if instance.blocked_by and instance.blocked_by != request.user:
                raise ServiceException(
                    f'Неможливо видалити. Обєкт заблокований "{instance.blocked_by.short_name}"')
        return super().destroy(request, *args, **kwargs)


class BaseReadOnlyOrganizationViewSetMixing(ReadOnlyModelViewSet, OrganizationFilterMixing, UserViewMixing):
    pass
