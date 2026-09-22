from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        post_migrate.connect(sync_declared_permissions, sender=self)


def sync_declared_permissions(**kwargs):
    from .models import RoutePermission
    from .modules.auth.permissions import DECLARED_PERMISSIONS as AUTH_PERMISSIONS
    from .modules.dashboard.permissions import (
        DECLARED_PERMISSIONS as DASHBOARD_PERMISSIONS,
    )
    from .modules.audit.permissions import (
        DECLARED_PERMISSIONS as AUDIT_PERMISSIONS,
    )
    from .modules.entities.permissions import (
        DECLARED_PERMISSIONS as ENTITY_PERMISSIONS,
    )
    from .modules.media.permissions import (
        DECLARED_PERMISSIONS as MEDIA_PERMISSIONS,
    )
    from .modules.articles.permissions import (
        DECLARED_PERMISSIONS as ARTICLE_PERMISSIONS,
    )
    from .modules.pages.permissions import DECLARED_PERMISSIONS as PAGE_PERMISSIONS

    declarations = (*AUTH_PERMISSIONS, *DASHBOARD_PERMISSIONS, *AUDIT_PERMISSIONS, *ENTITY_PERMISSIONS, *MEDIA_PERMISSIONS, *ARTICLE_PERMISSIONS, *PAGE_PERMISSIONS)
    declared_codes = {declaration["code"] for declaration in declarations}
    RoutePermission.objects.exclude(code__in=declared_codes).delete()
    for declaration in declarations:
        RoutePermission.objects.update_or_create(
            code=declaration["code"],
            defaults={
                "module": declaration["module"],
                "route": declaration["route"],
            },
        )
