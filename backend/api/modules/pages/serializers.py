import re

from django.core.validators import URLValidator

from ...models import ArticleCategory, DynamicForm, Page, PageComponent, PageComponentDefinition, PageTemplate


MODULE_TYPES = {"card", "form", "table", "modal"}
FORM_FIELD_TYPES = {"text", "textarea", "email", "number", "select", "checkbox", "date", "file"}
RESERVED_FORM_KEYS = {"id", "submit", "reset", "form", "data"}


def validate_form_fields(fields):
    if not isinstance(fields, list):
        return None, "Form fields must be an array."
    normalized = []
    keys = set()
    for index, field in enumerate(fields):
        if not isinstance(field, dict):
            return None, f"Field {index + 1} must be an object."
        key = str(field.get("key", "")).strip()
        label = str(field.get("label", "")).strip()
        field_type = str(field.get("type", "text")).strip()
        if not key or not label:
            return None, f"Field {index + 1} requires a key and label."
        if key.lower() in RESERVED_FORM_KEYS or key in keys or not key.replace("_", "").isalnum() or not key[0].isalpha():
            return None, f"Field key '{key}' is invalid or duplicated."
        if field_type not in FORM_FIELD_TYPES:
            return None, f"Field '{key}' has an unsupported type."
        options = field.get("options", [])
        if field_type == "select" and (not isinstance(options, list) or not options):
            return None, f"Select field '{key}' requires options."
        if field_type == "select":
            if any(not isinstance(option, dict) or not str(option.get("label", "")).strip() or not str(option.get("value", "")).strip() for option in options):
                return None, f"Select field '{key}' has invalid options."
            option_values = {str(option["value"]) for option in options}
            if field.get("default", "") not in ("", None) and str(field.get("default")) not in option_values:
                return None, f"Default value for select field '{key}' must match an option."
        rules = field.get("rules", {})
        if not isinstance(rules, dict):
            return None, f"Validation rules for '{key}' must be an object."
        if rules.get("pattern"):
            try:
                re.compile(str(rules["pattern"]))
            except re.error:
                return None, f"Validation pattern for '{key}' is invalid."
        normalized.append({
            "key": key,
            "label": label,
            "type": field_type,
            "placeholder": str(field.get("placeholder", "")),
            "default": field.get("default", ""),
            "options": options if field_type == "select" else [],
            "rules": {
                "required": bool(rules.get("required", False)),
                **({"min": rules["min"]} if "min" in rules else {}),
                **({"max": rules["max"]} if "max" in rules else {}),
                **({"pattern": str(rules["pattern"])} if rules.get("pattern") else {}),
            },
        })
        keys.add(key)
    return normalized, None


def serialize_form(form):
    return {"id": form.id, "name": form.name, "short_code": form.short_code, "description": form.description, "submit_url": form.submit_url, "fields": form.fields, "status": form.status, "created_at": form.created_at, "updated_at": form.updated_at}


def form_payload(data):
    name = str(data.get("name", "")).strip()
    short_code = str(data.get("short_code", "")).strip()
    submit_url = str(data.get("submit_url", "")).strip()
    fields, error = validate_form_fields(data.get("fields", []))
    status = str(data.get("status", Page.STATUS_DRAFT)).strip()
    if not name or not short_code:
        return None, "Form name and short code are required."
    if submit_url:
        try:
            URLValidator(schemes=["http", "https"])(submit_url)
        except Exception:
            return None, "Submit URL must be a valid HTTP or HTTPS URL."
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid form status."
    if error:
        return None, error
    return {"name": name, "short_code": short_code, "description": str(data.get("description", "")), "submit_url": submit_url, "fields": fields, "status": status}, None


def serialize_page(page):
    return {
        "id": page.id,
        "name": page.name,
        "slug": page.slug,
        "short_code": page.short_code,
        "template_key": page.template_key,
        "status": page.status,
        "components": page.components,
        "article_ids": page.article_ids,
        "content_config": page.content_config,
        "created_by": page.created_by.username if page.created_by else None,
        "created_at": page.created_at,
        "updated_at": page.updated_at,
        "template_id": page.template_id,
        "published_version_id": page.published_version_id,
        "draft_version_id": page.draft_version_id,
    }


def serialize_version(version, regions=None):
    return {
        "id": version.id,
        "page_id": version.page_id,
        "regions": version.regions if regions is None else regions,
        "version_number": version.version_number,
        "created_by": version.created_by.username if version.created_by else None,
        "created_at": version.created_at,
    }


def page_payload(data):
    name = str(data.get("name", "")).strip()
    slug = str(data.get("slug", "")).strip()
    template_key = str(data.get("template_key", "standard-page")).strip() or "standard-page"
    status = str(data.get("status", Page.STATUS_DRAFT)).strip()
    components = data.get("components", [])
    article_ids = data.get("article_ids", [])
    content_config = data.get("content_config", {})
    if not name:
        return None, "Page name is required."
    if not slug:
        return None, "Page slug is required."
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid page status."
    if not isinstance(components, list):
        return None, "Components must be an array."
    if not isinstance(article_ids, list) or any(not isinstance(item, int) for item in article_ids):
        return None, "Article IDs must be an array of numbers."
    if not isinstance(content_config, dict):
        return None, "Content configuration must be an object."
    content_mode = str(content_config.get("mode", "articles")).strip()
    if content_mode not in {"articles", "category", "editor", "form"}:
        return None, "Content mode must be articles, category, editor, or form."
    category_id = content_config.get("category_id")
    if content_mode == "category" and (not isinstance(category_id, int) or not ArticleCategory.objects.filter(pk=category_id, status=1).exists()):
        return None, "A valid article category is required."
    form_short_code = str(content_config.get("form_short_code", "")).strip()
    if content_mode == "form" and (not form_short_code or not DynamicForm.objects.filter(short_code=form_short_code, status=Page.STATUS_PUBLISHED).exists()):
        return None, "A published form shortcut is required."
    content_config = {**content_config, "mode": content_mode, "article_ids": article_ids}
    content_config["html"] = str(content_config.get("html", ""))
    content_config["css"] = str(content_config.get("css", ""))
    content_config["js"] = str(content_config.get("js", ""))
    content_config["form_short_code"] = form_short_code
    for component in components:
        if not isinstance(component, dict):
            return None, "Each component must be an object."
        if not str(component.get("name", "")).strip():
            return None, "Each component needs a name."
        modules = component.get("modules", [])
        if not isinstance(modules, list):
            return None, "Component modules must be an array."
        for module in modules:
            if not isinstance(module, dict) or module.get("type") not in MODULE_TYPES:
                return None, "Module type must be card, form, table, or modal."
    short_code = str(data.get("short_code") or slug).strip()[:120]
    return {"name": name, "slug": slug, "short_code": short_code, "template_key": template_key, "status": status, "components": components, "article_ids": article_ids, "content_config": content_config}, None


def serialize_template(template):
    return {
        "id": template.id,
        "name": template.name,
        "key": template.key,
        "regions": template.regions,
        "tokens": template.tokens,
        "status": template.status,
        "page_count": Page.objects.filter(template_key=template.key).exclude(status=Page.STATUS_ARCHIVED).count(),
        "affected_pages": list(Page.objects.filter(template_key=template.key).exclude(status=Page.STATUS_ARCHIVED).values("name", "slug")[:10]),
        "updated_at": template.updated_at,
    }


def serialize_component(component):
    return {
        "id": component.id,
        "name": component.name,
        "block_name": component.block_name,
        "short_code": component.short_code,
        "html": component.html,
        "css": component.css,
        "js": component.js,
        "content": component.content,
        "status": component.status,
        "created_at": component.created_at,
        "updated_at": component.updated_at,
    }


def component_payload(data):
    name = str(data.get("name", "")).strip()
    block_name = str(data.get("block_name", "")).strip()
    if not name or not block_name:
        return None, "Component name and block name are required."
    status = str(data.get("status", Page.STATUS_PUBLISHED)).strip()
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid component status."
    short_code = str(data.get("short_code") or block_name).strip()[:120]
    return {
        "name": name,
        "block_name": block_name,
        "short_code": short_code,
        "html": str(data.get("html", "")),
        "css": str(data.get("css", "")),
        "js": str(data.get("js", "")),
        "content": str(data.get("content", "")),
        "status": status,
    }, None


def serialize_component_definition(component):
    blocks = [
        {"block_name": block, "position": index + 1} if isinstance(block, str) else block
        for index, block in enumerate(component.blocks or [])
    ]
    return {
        "id": component.id,
        "name": component.name,
        "component_key": component.component_key,
        "short_code": component.short_code,
        "prehtml": component.prehtml,
        "html": component.html,
        "css": component.css,
        "js": component.js,
        "content": component.content,
        "backhtml": component.backhtml,
        "blocks": blocks,
        "status": component.status,
        "created_at": component.created_at,
        "updated_at": component.updated_at,
    }


def component_definition_payload(data):
    name = str(data.get("name", "")).strip()
    component_key = str(data.get("component_key", "")).strip()
    blocks = data.get("blocks", [])
    status = str(data.get("status", Page.STATUS_PUBLISHED)).strip()
    if not name or not component_key:
        return None, "Component name and key are required."
    if not isinstance(blocks, list):
        return None, "Component blocks must be an ordered array."
    normalized_blocks = []
    for index, block in enumerate(blocks):
        if isinstance(block, str) and block.strip():
            block_name = block.strip()
        elif isinstance(block, dict) and str(block.get("block_name", "")).strip():
            block_name = str(block["block_name"]).strip()
        else:
            return None, "Each component block needs a block name."
        if not PageComponent.objects.filter(block_name=block_name).exists():
            return None, f"Reusable block '{block_name}' does not exist."
        normalized_blocks.append({"block_name": block_name, "position": index + 1})
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid component status."
    short_code = str(data.get("short_code") or component_key).strip()[:120]
    return {
        "name": name,
        "component_key": component_key,
        "short_code": short_code,
        "prehtml": str(data.get("prehtml", "")),
        "html": str(data.get("html", "")),
        "css": str(data.get("css", "")),
        "js": str(data.get("js", "")),
        "content": str(data.get("content", "")),
        "backhtml": str(data.get("backhtml", "")),
        "blocks": normalized_blocks,
        "status": status,
    }, None


def template_payload(data):
    name = str(data.get("name", "")).strip()
    key = str(data.get("key", "")).strip()
    regions = data.get("regions", [])
    tokens = data.get("tokens", {})
    status = str(data.get("status", Page.STATUS_PUBLISHED)).strip()
    if not name or not key:
        return None, "Template name and key are required."
    if not isinstance(regions, list) or not isinstance(tokens, dict):
        return None, "Template regions and tokens have invalid formats."
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid template status."
    for region in regions:
        if not isinstance(region, dict) or not str(region.get("key", "")).strip():
            return None, "Each region needs a key."
        if region.get("locked") is not True and not isinstance(region.get("allowed_blocks", []), list):
            return None, "Region allowed blocks must be an array."
    return {"name": name, "key": key, "regions": regions, "tokens": tokens, "status": status}, None
