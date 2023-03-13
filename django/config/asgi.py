"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
# from apps.chat import urls as chat_urls
# from apps.notify import urls as notify_urls
# urls = chat_urls.websocket_urlpatterns+notify_urls.websocket_urlpatterns
# from apps.chat.middleware import TokenAuthMiddlewareStack
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": TokenAuthMiddlewareStack(
    #     URLRouter(urls)
    # ),
})
