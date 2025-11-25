import logging
import traceback
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django_tenants.utils import get_tenant_domain_model, tenant_context
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from jwt import decode as jwt_decode

User = get_user_model()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            if jwt_token_list := parse_qs(scope["query_string"].decode("utf8")).get("token", None):
                logging.info("ULANISHGA urinish")
                jwt_token = jwt_token_list[0]
                jwt_payload = self.get_payload(jwt_token)
                headers = scope.get("headers", [])
                host = list(filter(lambda x: x[0] == b"host", headers))
                if len(host) <= 0:
                    scope["user"] = AnonymousUser()
                else:
                    host = host[0][1].decode().split(":")[0]
                    TenantDomain = get_tenant_domain_model()
                    try:
                        domain = await TenantDomain.objects.select_related("tenant").aget(domain=host)
                        tenant = domain.tenant
                    except TenantDomain.DoesNotExist:
                        raise Exception("Tenant not found")
                    scope["tenant"] = tenant
                    scope["host"] = host
                    scope["user"] = await self.get_user(self.get_user_credentials(jwt_payload), tenant)
            else:
                scope["user"] = AnonymousUser()
        except (
            InvalidSignatureError,
            KeyError,
            ExpiredSignatureError,
            DecodeError,
        ) as e:
            logging.error(e)
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, pk, tenant):
        try:
            with tenant_context(tenant):
                return User.objects.select_related("station").get(id=pk)
        except User.DoesNotExist:
            return AnonymousUser()

    def get_payload(self, jwt_token):
        payload = jwt_decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload

    def get_user_credentials(self, payload):
        """
        method to get user credentials from jwt token payload.
        defaults to user id.
        """
        user_id = payload["user_id"]
        return user_id


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
