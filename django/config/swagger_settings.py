
SWAGGER_SETTINGS = {
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'delete', 'options', 'patch'],
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
