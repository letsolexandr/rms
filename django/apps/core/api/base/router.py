# -*- coding: utf-8 -*-

from django.conf.urls import *
from rest_framework import routers

from .serializers import (CoreOrganizationViewSet, LocalCoreOrganizationViewSet,
                           GetUserPermissions, GetRelatedObjects, RPC,
                          MultipleDelete, PermissionsViewSet, ContentTypeViewSet, GroupViewSet,GenderView)
from apps.core.api.base.viewsets import CoreUserViewSet, DepartmentViewSet
from .views import GetTaskResult

router = routers.DefaultRouter()

router.register(r'user', CoreUserViewSet)
router.register(r'gender', GenderView)
router.register(r'department', DepartmentViewSet)
router.register(r'permission', PermissionsViewSet)
router.register(r'content-type', ContentTypeViewSet)
router.register(r'organization', CoreOrganizationViewSet)
router.register(r'local-organization', LocalCoreOrganizationViewSet)

router.register(r'group', GroupViewSet)

urlpatterns = [
    url(r'user-permissions', GetUserPermissions.as_view()),
    url(r'get-celery-task/(?P<task_id>[^/.]+)', GetTaskResult.as_view()),
    url(r'get-related-objects', GetRelatedObjects),
    url(r'rpc', RPC),
    url(r'multiple-delete', MultipleDelete)

]

urlpatterns += router.urls
