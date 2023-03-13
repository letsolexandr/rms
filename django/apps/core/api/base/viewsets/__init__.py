import re
from django.core.exceptions import FieldError
from django_filters import rest_framework as filters
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import mixins
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from apps.core.api.base.serializers import CoreUserSerializer
from apps.core.models import CoreUser, Department
from ..serializers import CreateUserSerializer, ChangeUserPasswordSerializer, DepartmentSerializer, \
    DepartmentTreeSerializer, ProfileUserSerializer
from ....exceptions import ServiceException
from ....services.add_user_service import AddUserToOrg
from ....services.change_password_service import ChangePassword
from ....mixins.viewsets import BaseOrganizationViewSetMixing, DifferentSerializerMixin


class CoreUserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'options', 'patch']
    queryset = CoreUser.objects.prefetch_related(
        'user_permissions', 'groups', 'acting_main_persons').select_related(
        'organization', 'department')
    serializer_class = CoreUserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    ordering_fields = ['username', 'first_name', 'last_name', 'department__name', 'email',
                       'organization__full_name', 'is_active', 'group_names', 'acting']
    search_fields = ('username', 'first_name',
                     'last_name', 'organization__name')
    filterset_fields = {
        'organization': ['exact'],
        'department': ['exact'],
    }
    ordering = ('last_name', 'first_name')
    # DifferentSerializerMixin

    def get_queryset(self):
        from django.utils.timezone import localdate
        from django.db.models import Prefetch, Max, Q, Count, F, Case, Value, When, CharField
        from django.db.models.functions import Concat
        from django.db.models import Value, CharField
        from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
        if self.request.user.is_superuser:
            return self.queryset
        q = super(CoreUserViewSet, self).get_queryset()


        _now = localdate()
        acting = Max(
            'acting_main_persons__executor__short_name', filter=Q(acting_main_persons__start_date__lte=_now,
                                                                  acting_main_persons__end_date__gte=_now))
        acting_count = Count(
            'acting_main_persons__executor__short_name', filter=Q(acting_main_persons__start_date__lte=_now,
                                                                  acting_main_persons__end_date__gte=_now))
        concat_acting = Concat('short_name', Value(
            ' *(в.о - '), acting, Value(')'), output_field=CharField())
        __str__ = Case(
                When(acting_count=1, then=concat_acting),
                default=F('short_name'))
        q = q.annotate(group_names=StringAgg('groups__name', ', '))
        q = q.annotate(acting=acting).annotate(acting_count=acting_count).annotate(actings=acting).annotate(__str__sql = __str__)

        organization__id = self.request.user.organization_id
        
        # TODO додати властитвість для користувача - локальний адміністратор, перевірка групи це зайвий запит в базу
        if not self.request.user.groups.filter(code='ADMIN').exists():
            # Якщо не локальний адміністратор, показуємо лише активних (увімкнених користувачів)
            q = q.filter(is_active=True)
        try:
            filtered_q = q.filter(organization__id=organization__id)
        except FieldError:
            filtered_q = q
        except Exception as e:
            raise e
        return filtered_q

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            request_serializer = CreateUserSerializer(data=request.data)
            request_serializer.is_valid(raise_exception=True)
            process = AddUserToOrg(request, data=request_serializer.validated_data)
            res = process.run()
            serializer = CoreUserSerializer(res, context={'request': request})
            return Response(serializer.data)
        else:
            super(CoreUserViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        raise ServiceException('Видалення користувачів заборонене')

    def perform_update(self, serializer):
        # TODO Додати заборону на зміну доступів (не груп доступу) всім крім глобального адміністратора
        super(CoreUserViewSet, self).perform_update(serializer)

    @swagger_auto_schema(request_body=ChangeUserPasswordSerializer(),
                         responses={200: CoreUserSerializer(many=False)})
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Змінити пароль користувача. Замінити пароль може лише адмінітратор, або суперкористувач.
        Старий пароль не запитується.
        :param request:
        :return:
        """
        request_serializer = ChangeUserPasswordSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        process = ChangePassword(
            request, data=request_serializer.validated_data)
        res = process.run()
        serializer = CoreUserSerializer(res, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(  # request_body=ProfileUserSerializer(),
        responses={200: ProfileUserSerializer(many=False)}, methods=['GET', 'PATCH'])
    @action(detail=False, methods=['get', 'patch'], url_path='profile/self')
    def profile(self, request, pk=None):
        if request.method == "PATCH":
            # Змінити профіль користувача.
            user = request.user
            request_serializer = ProfileUserSerializer(
                instance=user, data=request.data)
            request_serializer.is_valid(raise_exception=True)
            request_serializer.save()
            serializer = ProfileUserSerializer(
                request_serializer.instance, context={'request': request})
            return Response(serializer.data)
        else:
            # ПРофіль користувача
            user = request.user
            serializer = ProfileUserSerializer(
                user, context={'request': request})
            return Response(serializer.data)

    def get_serializer_class(self):
        return super().get_serializer_class()

    @swagger_auto_schema(method='get')
    @action(detail=True, methods=['get'])
    def get_deleting_related_objects(self, request, pk=None):
        return PermissionDenied()


class DepartmentViewSet(BaseOrganizationViewSetMixing):
    queryset = Department.objects.select_related(
        'parent').prefetch_related('users').all()
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    serializer_class = DepartmentSerializer
    search_fields = ['name', ]

    @swagger_auto_schema(method='get', responses={200: DepartmentTreeSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Підпорядкована структура організації"""
        self.serializer_class = DepartmentTreeSerializer
        self.queryset = self.queryset.exclude(parent__isnull=False)
        return self.list(request)
