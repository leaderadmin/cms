from datetime import datetime, timezone as datetime_timezone
from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from ...models import AuthSession


def client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded_for.split(",")[0] if forwarded_for else request.META.get("REMOTE_ADDR"))


def token_expiry(token):
    return datetime.fromtimestamp(token["exp"], tz=datetime_timezone.utc)


def blacklist_refresh_jti(jti):
    try:
        outstanding = OutstandingToken.objects.get(jti=jti)
    except OutstandingToken.DoesNotExist:
        return
    BlacklistedToken.objects.get_or_create(token=outstanding)


def revoke_session(session):
    if session.revoked_at is None:
        session.revoked_at = timezone.now()
        session.save(update_fields=("revoked_at",))
    blacklist_refresh_jti(session.refresh_jti)


def create_session(user, request):
    active_sessions = list(
        AuthSession.objects.filter(
            user=user,
            revoked_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).order_by("created_at")
    )
    max_sessions = settings.AUTH_MAX_SESSIONS
    for old_session in active_sessions[max(0, max_sessions - 1) :]:
        revoke_session(old_session)

    session_id = uuid4()
    refresh = RefreshToken.for_user(user)
    refresh["sid"] = str(session_id)
    session = AuthSession.objects.create(
        session_id=session_id,
        user=user,
        refresh_jti=refresh["jti"],
        expires_at=token_expiry(refresh),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        ip_address=client_ip(request),
    )
    return session, refresh