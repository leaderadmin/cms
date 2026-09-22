from rest_framework.permissions import BasePermission


AUDIT_LOGS_READ = "audit.logs.read"

DECLARED_PERMISSIONS = (
    {
        "code": AUDIT_LOGS_READ,
        "module": "audit",
        "route": "GET /api/audit/logs/",
    },
)


class CanReadActivityLogs(BasePermission):
    message = "You do not have permission to view activity logs."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.dynamic_roles.filter(
            permissions__code=AUDIT_LOGS_READ
        ).exists()