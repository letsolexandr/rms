# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import  Q, F
from django.db.models import Value, CharField
import json
import logging
from typing import Dict


from django.apps import apps
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import JsonResponse
from django.http.request import HttpRequest
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers, viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max

from django.contrib.postgres.aggregates import ArrayAgg, StringAgg

from apps.core.mixins.viewsets import BaseViewSetMixing, BaseOrganizationViewSetMixing
from ...mixins.serializers import DetailSerializerMixin
from ...models import  CoreUser, CoreOrganization, Department, CHANGE_ORG_PROFILE_PERMISSION
from ...mixins.serializers import RecursiveField
logger = logging.getLogger(__name__)

SUPERUSER_ID = 1


class LCorePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return instance.natural_key

    def to_representation(self, value):
        return value.natural_key


class DynamicFieldsModelSerializer(FlexFieldsModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        # print('__init__')

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        self.set_write_only_fields()

    def _clean_fields(self, omit_fields, sparse_fields, next_level_omits):
        f = self.fields
        super(DynamicFieldsModelSerializer, self)._clean_fields(
            omit_fields, sparse_fields, next_level_omits)

    def set_write_only_fields(self):
        meta = self.Meta
        if hasattr(meta, 'write_only_fields'):
            write_only_fields = self.Meta.write_only_fields

            for field in self.fields.values():
                if field.field_name in write_only_fields:
                    field.write_only = True
                    print(field.field_name)

    def get_field_names(self, declared_fields, info):
        request = self.context.get('request')
        if request:
            fields_ext = self.context['request'].query_params.get('fields')
        else:
            fields_ext = None

        if fields_ext:
            fields_ext = fields_ext.split(',')
        else:
            fields_ext = []
        fields = super(DynamicFieldsModelSerializer,
                       self).get_field_names(declared_fields, info)
        result_list = list(set(fields_ext) | set(fields))
        return result_list

    def get_uniqueness_extra_kwargs(self, field_names, declared_fields, extra_kwargs):
        fields = super(DynamicFieldsModelSerializer, self).get_uniqueness_extra_kwargs(field_names, declared_fields,
                                                                                       extra_kwargs)
        return fields

    def build_property_field(self, field_name, model_class):
        field_class, field_kwargs = super(DynamicFieldsModelSerializer, self).build_property_field(field_name,
                                                                                                   model_class)
        return field_class, field_kwargs


# CoreUser-------------------------------------------------------


class ListCoreUserSerializer(serializers.ListSerializer):
    list_fields = ['id', 'username', 'first_name', 'last_name', 'department__name', 'email', 'photo', 'av_color',
                   'organization__full_name', 'is_active',
                ##annotate_fields
                'group_names','acting',
                   ]

    # TODO винести на ревю, зробити елегантнішим способом
    def to_representation(self, data):
        # _now = localdate()
        # acting = Max(
        #     'acting_main_persons__executor__short_name', filter=Q(acting_main_persons__start_date__lte=_now,
        #                                                           acting_main_persons__end_date__gte=_now))
        # acting_count = Count(
        #     'acting_main_persons__executor__short_name', filter=Q(acting_main_persons__start_date__lte=_now,
        #                                                           acting_main_persons__end_date__gte=_now))
        # concat_acting = Concat('short_name', Value(
        #     ' *(в.о - '), acting, Value(')'), output_field=CharField())
        # __str__ = Case(
        #         When(acting_count=1, then=concat_acting),
        #         default=F('short_name'))
        q = data.object_list
        q = q.values(*self.list_fields)
        # q = q.annotate(groups=StringAgg('groups__name', ', '))
        # q = q.annotate(acting=acting).annotate(acting_count=acting_count).annotate(actings=acting).annotate(__str__ = __str__)
        # q = q.annotate(__str__=F('short_name'))
        #q = q.annotate(actings=F('acting_main_persons__executor__short_name'))

        # q = q.annotate(__str__=Concat('short_name',Value(', в.о-') ,Max(
        #     'acting_main_persons__executor__short_name',filter=Q(acting_main_persons__start_date__lte=_now,
        #                 acting_main_persons__end_date__gte=_now)),
        #          output_field=CharField()))
        q = q.annotate(__str__=F('__str__sql'))
        return list(q)


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=CoreOrganization.objects.all(), required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)


class ChangeUserPasswordSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CoreUser.objects.all())
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoreUser
        #list_serializer_class = ListCoreUserSerializer
        db_fields = ['id', 'first_name', 'last_name', 'photo',]
        fields = db_fields+['__str__']


class ProfileUserSerializer(serializers.ModelSerializer):
    department_name = serializers.StringRelatedField(source='department')

    class Meta:
        model = CoreUser
        fields = (
            'id',  'email', '__str__', 'photo', 'phone', 'username', 'first_name', 'last_name',
             'state', 'department_name', 'cached_permissions')
        read_only_fields = ['__str__', 'id',
                            'username', 'first_name', 'last_name', 'cached_permissions']


class FlatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreUser
        fields = ('short_name',)


class CoreUserSerializer(serializers.ModelSerializer):
    org_name = serializers.SerializerMethodField(method_name='orgname')
    # group_on_login_redirect = serializers.SerializerMethodField()
    acting_main_person = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source='department', read_only=True)
    group_list = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
        source="groups"
    )

    __str__ = serializers.SerializerMethodField(method_name='get_combine_name')

    class Meta:
        model = CoreUser
        list_serializer_class = ListCoreUserSerializer
        fields = (
            'id', 'username', 'department', 'first_name', 'last_name', 'email', 'ipn', 'last_login', 'state',
            # 'group_on_login_redirect',
            'is_active', 'is_superuser', 'group_list', 'acting_main_person',
            'photo',
            'groups', 'user_permissions', 'department_name',
            'organization', 'org_name',
            '__str__'
        )
        read_only_fields = ['id', 'department_name',
                            'is_superuser', 'acting_main_person', 'last_login']

    def orgname(self, obj):
        return obj.organization.__str__() if obj.organization else None

    def get_acting_main_person(self, obj):
        q = obj.acting_executors.get_actual_data()
        if q.exists():
            return ', '.join([acting.main_person.short_name for acting in q])

    def get_combine_name(self, obj):
        q = obj.acting_main_persons.get_actual_data()
        name = obj.__str__()
        if q.exists():
            executors = ', '.join([acting.executor.short_name for acting in q])
            return f'{name}(в.о. {executors})'
        return obj.__str__()

    # def to_representation(self, *args, **kwargs):
    #     repr = super().to_representation(*args, **kwargs)
    #     return repr

    # def data(self):
    #     return super().data


# -------------------------------------------------------------


# -------------------------------------------------------------


# ContentType-------------------------------------------------------
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ('app_label', 'model', '__str__', 'id',)


# ViewSets define the view behavior.
class ContentTypeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'options']
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ('app_label', 'model')


# -------------------------------------------------------------
# Permissions-------------------------------------------------------
class PermissionsSerializer(DynamicFieldsModelSerializer):
    content_type_data = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Permission
        fields = ('name', 'content_type', 'content_type_data',
                  'codename', '__str__', 'id',)
        expandable_fields = {
            'content_type_data': (
                ContentTypeSerializer, {'source': 'content_type', })
        }

    def __str__(self):
        return self.name


# ViewSets define the view behavior.
class PermissionsViewSet(BaseOrganizationViewSetMixing):
    http_method_names = ['get', 'post', 'delete', 'options', 'patch']
    permit_list_expands = ['content_type_data']
    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ('name', 'codename')


# -------------------------------------------------------------


# CoreOrganization-------------------------------------------------------
class CoreOrganizationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CoreOrganization
        fields = [
            'name', 'full_name', 'edrpou', 'gender','__str__', 'id', 'status', 'register_date', 'sev_connected', 'org_type']


class SimpleCoreOrganizationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CoreOrganization
        fields = [
            'name', 'full_name', 'edrpou','gender', '__str__', 'id',  'org_type']


class CoreOrganizationDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CoreOrganization
        fields = [
            'name', 'full_name','gender',
            'region', 'district', 'settlement', 'settlement_name', 'street_type', 'street', 'street_name',
            'house_number', 'build_number',
            'apartment_number', 'zip_code',
            'address',
            'edrpou', 'phone', 'fax', 'email', 'site', 'work_reason',
            'org_type',
            'sev_connection_type', 'sev_sed_connected', 'group_organization', '__str__', 'id', 'status',
            'register_date', 'sert_name', 'main_unit', 'main_unit_state', 'main_activity_text', 'settlement_account',
            'note', 'mfo',
            'certificate_number', 'bank_name', 'bank', 'ipn', 'statute_copy', 'system_password', 'system_id',
            'sev_connected']

    def validate_edrpou_value(self, attrs):
        if self.instance:
            return
        edrpou = attrs.get('edrpou')
        organization_id = self.context.get('request').user.organization_id
        if CoreOrganization.objects.filter(organization_id=organization_id, edrpou=edrpou).exists():
            raise ValidationError({
                'edrpou': 'Такий ідентифікатор вже існує, призначте інший ідентифікатор'})

    def validate(self, attrs):
        self.validate_edrpou_value(attrs)
        return super(CoreOrganizationDetailSerializer, self).validate(attrs)


class ProfileCoreOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreOrganization
        fields = (
            'phone', 'fax', 'email', 'site', 'id','gender',
            'name', 'full_name', 'main_unit', 'main_unit_state', 'settlement_account',
            'note', 'mfo', 'bank_name', 'bank',  'statute_copy', 'logo_img'
        )
        read_only_fields = ['id']



# ViewSets define the view behavior.
class CoreOrganizationViewSet(DetailSerializerMixin, BaseViewSetMixing):
    http_method_names = ['get', 'post', 'delete', 'options', 'patch']
    queryset = CoreOrganization.objects.all()
    serializer_class = CoreOrganizationDetailSerializer  # CoreOrganizationSerializer
    serializer_detail_class = CoreOrganizationDetailSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ['full_name', 'address', 'edrpou','name']
    filterset_fields = {'id': ['in'],
                        'bank': ['exact']}

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset

        organization__id = self.request.user.organization_id
        q = super(CoreOrganizationViewSet, self).get_queryset()

        try:
            filtered_q = q.filter(Q(organization__id=organization__id) | Q(organization__id=SUPERUSER_ID)).exclude(
                id=organization__id)
        except FieldError:
            filtered_q = q
        except Exception as e:
            raise e
        return filtered_q

    def get_serializer_class(self):
        default_serializer = super().get_serializer_class()
        if self.request.user.is_superuser:
            return default_serializer
        return SimpleCoreOrganizationSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()

    #     if request.user.is_superuser:
    #         return super(CoreOrganizationViewSet, self).retrieve(request, *args, **kwargs)

    #     if request.user.organization_id != instance.organization_id:
    #         self.permission_denied(request)

    #     return super(CoreOrganizationViewSet, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser:
            return super(CoreOrganizationViewSet, self).update(request, *args, **kwargs)

        if request.user.organization_id != instance.organization_id:
            self.permission_denied(request)

        return super(CoreOrganizationViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mode = request.GET.get('mode')
        if request.user.organization_id == instance.organization:
            self.permission_denied(request)

        if request.user.is_superuser:
            self.perform_destroy(instance, mode)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if request.user.organization_id != instance.organization_id:
                self.permission_denied(request)
            else:
                self.perform_destroy(instance, mode)
                return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=ProfileCoreOrganizationSerializer(),
                         responses={200: ProfileCoreOrganizationSerializer(many=False)})
    @action(detail=False, methods=['post'])
    def change_profile(self, request):
        """
        Змінити профіль організації.
        :param request:
        :return: Response
        """
        required_permission = 'core.'+CHANGE_ORG_PROFILE_PERMISSION
        if not request.user.has_perm(required_permission):
            self.permission_denied(request)

        organization = request.user.organization

        request_serializer = ProfileCoreOrganizationSerializer(
            instance=organization, data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_serializer.save()
        serializer = ProfileCoreOrganizationSerializer(
            request_serializer.instance, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: ProfileCoreOrganizationSerializer(many=False)})
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Профіль організації.
        :param request:
        :return: Response
        """
        organization = request.user.organization
        serializer = ProfileCoreOrganizationSerializer(
            organization, context={'request': request})
        return Response(serializer.data)


# -------------------------------------------------------------
class LocalCoreOrganizationViewSet(CoreOrganizationViewSet):
    """Повертає перелік організацій створений від імені організації запитувача"""
    http_method_names = ['get', 'post', 'delete', 'options', 'patch']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset

        organization__id = self.request.user.organization_id
        q = super(LocalCoreOrganizationViewSet, self).get_queryset()

        try:
            filtered_q = q.filter(organization__id=organization__id).exclude(
                id=organization__id)
        except FieldError:
            filtered_q = q
        except Exception as e:
            raise e
        return filtered_q


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', '__str__', 'id', #'permissions',
                  'order', 'code', 'on_login_redirect_path']


# ViewSets define the view behavior.
class GroupViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'options', 'patch']
    #viewsets.ModelViewSet.pagination_class.page_size = 100
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ['name']
    filterset_fields = {
            'id': ['in'],
        }
    


# -------------------------------------------------------------


class GetUserPermissions(APIView):
    permission_classes = [IsAuthenticated]

    def get_acting_permission(self, user):
        user_permissions = list(user.get_all_permissions())
        acting_users = user.acting_executors.get_actual_data()
        for acting_user in acting_users.all():
            user_permissions += list(acting_user.main_person.get_all_permissions())

        # get usnique permissions
        unique_user_permissions = set(user_permissions)
        return list(unique_user_permissions)

    def get(self, request):
        user = request.user
        _permissions = self.get_acting_permission(user)
        permissions = [perm.split('.')[1] for perm in _permissions]

        user_data = CoreUser.objects.select_related(
            'organization').get(id=user.id)
        return JsonResponse({'permissions': permissions,
                             'user': CoreUserSerializer(user_data).data,
                             })


app_label = openapi.Parameter('app_label', openapi.IN_QUERY, description="Name of application",
                              type=openapi.TYPE_STRING, required=True)
model = openapi.Parameter('model', openapi.IN_QUERY,
                          description=" data model", type=openapi.TYPE_STRING, required=True)
method = openapi.Parameter('method', openapi.IN_QUERY, description="method to call", type=openapi.TYPE_STRING,
                           required=True)
pk = openapi.Parameter('pk', openapi.IN_QUERY,
                       description="object primary key", type=openapi.TYPE_INTEGER)
params = openapi.Parameter('params', openapi.IN_QUERY, description="stringify params pass to method",
                           type=openapi.TYPE_STRING)


@swagger_auto_schema(method='get', manual_parameters=[app_label, model, method, pk, params])
@api_view(['GET'])
def RPC(request):
    model_name = request.GET.get('model')
    app_label = request.GET.get('app_label')
    model_method = request.GET.get('method')
    _params = request.GET.get('params')
    params = json.loads(_params) if _params else None
    pk = request.GET.get('pk')
    model = apps.get_model(app_label=app_label, model_name=model_name)
    result = {}
    if pk:
        obj = model.objects.get(pk=pk)
        if hasattr(obj, model_method):
            method = getattr(obj, model_method)

            if params:
                result['data'] = method(params)
            else:
                result['data'] = method()

            result['status'] = 'success'
        else:
            result['status'] = 'error'
            result['message'] = 'method "{}" is not exist '.format(
                model_method)

    else:
        if hasattr(model, model_method):
            class_method = getattr(model, model_method)

            if params:
                result['data'] = class_method(params)
            else:
                result['data'] = class_method()
            result['status'] = 'success'
        else:
            result['status'] = 'error'
            result['message'] = 'class method "{}" is not exist '.format(
                model_method)

    return JsonResponse({'result': result})


##########################################################################################

ids = openapi.Parameter('ids[]', openapi.IN_QUERY, description="list of ids", type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_INTEGER))
request_q = openapi.Parameter(
    'request_q', openapi.IN_QUERY, description="list of ids", type=openapi.TYPE_OBJECT)
delete_all_in_query = openapi.Parameter('delete_all_in_query', openapi.IN_QUERY, description="list of ids",
                                        type=openapi.TYPE_BOOLEAN)


@swagger_auto_schema(method='get', manual_parameters=[app_label, model, request_q, ids, delete_all_in_query])
@api_view(['GET'])
def MultipleDelete(request: HttpRequest):
    result = {}
    model_name = request.GET.get('model')
    if not model_name:
        raise APIException('"model_name" is required!')

    app_label = request.GET.get('app_label')
    if not app_label:
        raise APIException('"app_label" is required!')
    request_q: Dict = {}
    delete_all_in_query: bool = json.loads(
        request.GET.get('delete_all_in_query', 'false'))
    _ids = request.GET.getlist('ids[]')
    ids = [int(item) for item in _ids]
    if not delete_all_in_query:
        request_q.update({"pk__in": ids})
    model = apps.get_model(app_label=app_label, model_name=model_name)
    queryset = model.objects.filter(**request_q)
    result['delete_count'] = queryset.count()
    result['status'] = 'success'
    result['status_ua'] = 'Успішно'
    result['message'] = f'Успішно видадено {result["delete_count"]} записів'
    queryset.delete()
    return JsonResponse({'result': result})

# TODO видалити


@api_view(['GET'])
def GetRelatedObjects(request):
    obj_id = (request.GET.get('id', 0))
    if not obj_id:
        raise APIException('"obj_id" is required!')
    model_name = request.GET.get('model_name')
    if not model_name:
        raise APIException('"model_name" is required!')

    app_label = request.GET.get('app_label')
    if not app_label:
        raise APIException('"app_label" is required!')

    model = apps.get_model(app_label=app_label, model_name=model_name)
    obj = model.objects.get(pk=(obj_id))
    name = obj._meta.verbose_name
    related_fields = obj._meta.related_objects
    related_list = []
    for related in related_fields:
        field_name = related.get_cache_name()
        if hasattr(obj, field_name):
            related_field = getattr(obj, field_name)
            if hasattr(related_field, 'all'):
                queryset = related_field.all()
                for item in queryset:
                    related_list.append({'id': item.id, 'name': str(item)})
            else:
                related_list.append(str(related_field))
    return JsonResponse({'name': name, 'id': obj_id, 'children': related_list})


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, allow_null=True, source='childs')
    users_data = SimpleUserSerializer(
        many=True, allow_null=True, source='users')

    class Meta():
        model = Department
        fields = ['id', 'code', 'name', 'children', 'users_data']


class DepartmentSerializer(DynamicFieldsModelSerializer):
    parent_name = serializers.SerializerMethodField()

    def get_parent_name(self, obj):
        if obj.parent:
            return str(obj.parent)
        else:
            return "Не вказано"

    class Meta:
        model = Department
        fields = ['name', 'code', '__str__', 'id',
                  'parent', 'parent_name', 'department_type']
