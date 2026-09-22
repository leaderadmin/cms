from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from drf_spectacular.extensions import OpenApiAuthenticationExtension

from ...models import AuthSession


class SessionJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        session_id = token.get("sid")
        if not session_id:
            raise AuthenticationFailed("Token is not linked to an active session.")
        try:
            session = AuthSession.objects.get(session_id=session_id, user=user)
        except (AuthSession.DoesNotExist, ValueError):
            raise AuthenticationFailed("Session is not valid.")
        if not session.is_active:
            raise AuthenticationFailed("Session has expired or been revoked.")
        AuthSession.objects.filter(session_id=session.session_id).update(
            last_seen_at=timezone.now()
        )
        return result

class SessionJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "api.modules.auth.authentication.SessionJWTAuthentication"
    name = "BearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }