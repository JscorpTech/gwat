# type: ignore
import os
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from channels.security.websocket import AllowedHostsOriginValidator  # noqa

from config.env import env  # noqa
from core.apps.websocket.urls import websocket_urlpatterns  # noqa
from core.apps.websocket.middlewares import JWTAuthMiddlewareStack  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env("DJANGO_SETTINGS_MODULE"))  # noqa


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    }
)
