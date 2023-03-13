REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser'
        # ...
    ),
    'DEFAULT_RENDERER_CLASSES': (
        #"apps.core.renders.SimpleJSONRenderer",
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
        # 'drf_renderer_xlsx.renderers.XLSXRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'apps.core.metadata.LCoreSimpleMetadata',
    

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
   'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.LCOREPagination',
    'PAGE_SIZE': 5,

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
    ),
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
        ##'apps.core.permissions.AllowOptionsAuthentication',
        ##'rest_framework.permissions.DjangoModelPermissions',
        ##'core.permissions.LCoreDjangoModelPermissions',
    ],
}

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
}
