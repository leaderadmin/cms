import json
import os
import socket
import traceback
import uuid
from time import monotonic

from django.utils import timezone

from .models import ActivityLog


class ActivityLogMiddleware:
    excluded_paths = ("/api/schema/", "/api/docs/", "/api/redoc/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = monotonic()
        request.activity_context = {
            "request_id": request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4()),
            "trace_id": request.META.get("HTTP_X_TRACE_ID"),
        }
        response = None
        exception = None
        try:
            response = self.get_response(request)
        except Exception as error:
            exception = error
        if request.path.startswith("/api/") and not request.path.startswith(self.excluded_paths):
            try:
                user = getattr(request, "user", None)
                context = request.activity_context
                event = self._classify(request, response, exception)
                ActivityLog.objects.create(
                    timestamp=event["timestamp"],
                    level=event["level"],
                    service=os.getenv("SERVICE_NAME", "startup-api"),
                    module=event["module"],
                    environment=os.getenv("APP_ENV", "development"),
                    host=socket.gethostname(),
                    message=event["message"],
                    trace_id=context.get("trace_id"),
                    request_id=context.get("request_id"),
                    session_id=self._session_id(request),
                    user=(user if user and user.is_authenticated else None),
                    action=event["action"],
                    entity_type=event["entity_type"],
                    entity_id=context.get("entity_id"),
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code if response is not None else 500,
                    error_code=event["error_code"],
                    error_type=event["error_type"],
                    stack_trace="".join(traceback.format_exception(exception)) if exception else None,
                    changed_fields=context.get("changed_fields", []),
                    duration_ms=max(0, round((monotonic() - started_at) * 1000)),
                    ip_address=self._client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
                    portal_id=context.get("portal_id"),
                    tags=event["tags"],
                )
            except Exception:
                pass
        if exception:
            raise exception
        return response

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def _session_id(request):
        auth = getattr(request, "auth", None)
        return str(auth.get("sid")) if auth and auth.get("sid") else None

    @staticmethod
    def _classify(request, response, exception=None):
        path_parts = [part for part in request.path.strip("/").split("/") if part]
        module = path_parts[1] if len(path_parts) > 1 and path_parts[0] == "api" else "api"
        resource = path_parts[2] if len(path_parts) > 2 and path_parts[0] == "api" else "request"
        action = f"{module}.{resource}.{request.method.lower()}"
        route_key = request.path.rstrip("/")
        known_actions = {
            "/api/auth/login": ("auth.login", "User"),
            "/api/auth/register": ("auth.register", "User"),
            "/api/auth/logout": ("auth.logout", "AuthSession"),
            "/api/auth/token/refresh": ("auth.token_refresh", "AuthSession"),
            "/api/stats": ("dashboard.stats.read", "Dashboard"),
            "/api/health": ("dashboard.health.read", "Health"),
            "/api/audit/logs": ("audit.activity_logs.list", "ActivityLog"),
        }
        action, entity_type = known_actions.get(route_key, (action, resource.title()))
        status_code = response.status_code if response is not None else 500
        level = "ERROR" if status_code >= 500 or exception else "WARNING" if status_code >= 400 else "INFO"
        error_code = None
        error_type = None
        error_message = None
        try:
            payload = json.loads(response.content.decode("utf-8")) if response is not None else {}
            if status_code >= 400 and isinstance(payload, dict):
                error_code = payload.get("code") or payload.get("detail")
                error_type = payload.get("type")
                error_message = payload.get("message") or payload.get("detail")
        except (AttributeError, ValueError, UnicodeDecodeError):
            pass
        if status_code >= 400 and not error_code:
            reason = getattr(response, "reason_phrase", "Error") if response is not None else "Internal Server Error"
            error_code = f"HTTP_{status_code}"
            error_type = "HTTPError"
            error_message = f"HTTP {status_code} {reason}"
        event = {
            "timestamp": timezone.now(),
            "level": level,
            "module": module,
            "message": action,
            "action": action,
            "entity_type": entity_type,
            "error_code": str(error_code)[:120] if error_code else None,
            "error_type": str(error_type)[:120] if error_type else None,
            "tags": [module, resource],
        }
        if exception:
            event["message"] = str(exception)[:255] or exception.__class__.__name__
            event["error_type"] = exception.__class__.__name__
        elif status_code >= 400:
            event["message"] = str(error_message or error_code or error_type or action)[:255]
        context = getattr(request, "activity_context", {})
        for field in ("level", "module", "message", "action", "entity_type", "entity_id", "error_code", "error_type", "tags"):
            if field in context:
                event[field] = context[field]
        return event