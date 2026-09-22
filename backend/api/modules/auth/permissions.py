from rest_framework.permissions import BasePermission


# Every auth administration permission is declared here and referenced by its view.
AUTH_ME = "auth.me.read"
AUTH_ROLES_READ = "auth.roles.read"
AUTH_ROLES_CREATE = "auth.roles.create"
AUTH_ROLES_UPDATE = "auth.roles.update"
AUTH_ROLES_DELETE = "auth.roles.delete"
AUTH_PERMISSIONS_READ = "auth.permissions.read"
AUTH_USERS_READ = "auth.users.read"
AUTH_USERS_CREATE = "auth.users.create"
AUTH_USERS_UPDATE = "auth.users.update"
AUTH_USERS_ASSIGN_ROLE = "auth.users.assign_role"
AUTH_SESSIONS_READ = "auth.sessions.read"
AUTH_SESSIONS_REVOKE = "auth.sessions.revoke"
AUTH_MENU_READ = "auth.menu.read"
AUTH_MENU_CREATE = "auth.menu.create"
AUTH_MENU_UPDATE = "auth.menu.update"
AUTH_MENU_DELETE = "auth.menu.delete"

DECLARED_PERMISSIONS = (
    {
        "code": AUTH_ME,
        "module": "auth",
        "route": "GET /api/auth/me/",
    },
    {
        "code": AUTH_ROLES_READ,
        "module": "auth",
        "route": "GET /api/auth/roles/",
    },
    {
        "code": AUTH_ROLES_CREATE,
        "module": "auth",
        "route": "POST /api/auth/roles/",
    },
    {
        "code": AUTH_ROLES_UPDATE,
        "module": "auth",
        "route": "PATCH /api/auth/roles/<id>/",
    },
    {
        "code": AUTH_ROLES_DELETE,
        "module": "auth",
        "route": "DELETE /api/auth/roles/<id>/",
    },
    {
        "code": AUTH_PERMISSIONS_READ,
        "module": "auth",
        "route": "GET /api/auth/permissions/",
    },
    {
        "code": AUTH_USERS_READ,
        "module": "auth",
        "route": "GET /api/auth/users/",
    },
    {
        "code": AUTH_USERS_CREATE,
        "module": "auth",
        "route": "POST /api/auth/users/",
    },
    {
        "code": AUTH_USERS_UPDATE,
        "module": "auth",
        "route": "PATCH /api/auth/users/<id>/",
    },
    {
        "code": AUTH_USERS_ASSIGN_ROLE,
        "module": "auth",
        "route": "POST /api/auth/users/<id>/roles/",
    },
    {
        "code": AUTH_SESSIONS_READ,
        "module": "auth",
        "route": "GET /api/auth/sessions/",
    },
    {
        "code": AUTH_SESSIONS_REVOKE,
        "module": "auth",
        "route": "POST /api/auth/sessions/<id>/revoke/",
    },
    {"code": AUTH_MENU_READ, "module": "auth", "route": "GET /api/auth/menu/"},
    {"code": AUTH_MENU_CREATE, "module": "auth", "route": "POST /api/auth/menu/"},
    {"code": AUTH_MENU_UPDATE, "module": "auth", "route": "PATCH /api/auth/menu/<id>/"},
    {"code": AUTH_MENU_DELETE, "module": "auth", "route": "DELETE /api/auth/menu/<id>/"},
)


class HasRoutePermission(BasePermission):
    message = "You do not have permission to access this route."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        required_permissions = getattr(view, "required_permissions", {})
        required_permission = required_permissions.get(
            request.method,
            getattr(view, "required_permission", None),
        )
        if not required_permission:
            return False
        return request.user.dynamic_roles.filter(
            permissions__code=required_permission
        ).exists()
