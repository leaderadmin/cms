from django.contrib.auth.models import User
from django.db import models

from ...models import (
    ActivityLog,
    AuthSession,
    EmailConfiguration,
    EmailTemplate,
    MenuItem,
    Role,
    RoutePermission,
    UserProfile,
)


ENTITY_MODELS = {
    "user": ("Users", User),
    "role": ("Roles", Role),
    "route-permission": ("Route permissions", RoutePermission),
    "menu-item": ("Menu items", MenuItem),
    "user-profile": ("User profiles", UserProfile),
    "auth-session": ("Auth sessions", AuthSession),
    "activity-log": ("Activity logs", ActivityLog),
    "email-configuration": ("Email configuration", EmailConfiguration),
    "email-template": ("Email templates", EmailTemplate),
}


HIDDEN_FIELDS = {"password", "refresh_jti", "stack_trace"}
READ_ONLY_MODELS = {"auth-session", "activity-log"}


def get_entity(slug):
    return ENTITY_MODELS.get(slug)


def field_metadata(model, slug):
    fields = []
    for field in model._meta.fields:
        if field.name in HIDDEN_FIELDS:
            continue
        fields.append({
            "name": field.name,
            "label": field.verbose_name.replace("_", " ").title(),
            "type": field.get_internal_type(),
            "required": not field.blank and not field.null and not field.auto_created and field.default is models.NOT_PROVIDED,
            "read_only": field.primary_key or field.auto_created or getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False) or slug in READ_ONLY_MODELS,
            "relation": field.is_relation,
            "choices": [{"value": value, "label": label} for value, label in field.choices] if field.choices else [],
        })
    return fields