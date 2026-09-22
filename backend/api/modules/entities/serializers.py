from django.core.exceptions import ValidationError
from django.db import models

from .registry import HIDDEN_FIELDS, READ_ONLY_MODELS


def serialize_record(instance):
    values = {}
    for field in instance._meta.fields:
        if field.name in HIDDEN_FIELDS:
            continue
        value = getattr(instance, field.attname if field.is_relation else field.name)
        if isinstance(field, (models.DateField, models.DateTimeField)):
            value = value.isoformat() if value else None
        values[field.name] = value
    return values


def save_record(model, slug, payload, instance=None):
    if slug in READ_ONLY_MODELS:
        raise ValidationError("This table is read-only.")
    target = instance or model()
    allowed = {field.name: field for field in model._meta.fields if field.name not in HIDDEN_FIELDS}
    for name, value in payload.items():
        field = allowed.get(name)
        if not field or field.primary_key or field.auto_created or getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            continue
        setattr(target, name, field.to_python(value))
    target.full_clean()
    target.save()
    return target