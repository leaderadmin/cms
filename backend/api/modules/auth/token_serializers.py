from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from ...models import AuthSession
from .sessions import token_expiry


class SessionTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        old_refresh = RefreshToken(attrs["refresh"])
        session_id = old_refresh.get("sid")
        session = AuthSession.objects.filter(session_id=session_id).first()
        if session is None or not session.is_active:
            raise ValidationError("Session has expired or been revoked.")

        data = super().validate(attrs)
        new_refresh = RefreshToken(data["refresh"])
        new_refresh["sid"] = str(session.session_id)
        data["refresh"] = str(new_refresh)
        session.refresh_jti = new_refresh["jti"]
        session.expires_at = token_expiry(new_refresh)
        session.save(update_fields=("refresh_jti", "expires_at", "last_seen_at"))
        return data