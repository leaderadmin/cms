from ...models import Page, PageComponent, PageComponentDefinition, PageTemplate


MODULE_TYPES = {"card", "form", "table", "modal"}


def serialize_page(page):
    return {
        "id": page.id,
        "name": page.name,
        "slug": page.slug,
        "template_key": page.template_key,
        "status": page.status,
        "components": page.components,
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
    if not name:
        return None, "Page name is required."
    if not slug:
        return None, "Page slug is required."
    if status not in {choice[0] for choice in Page.STATUS_CHOICES}:
        return None, "Invalid page status."
    if not isinstance(components, list):
        return None, "Components must be an array."
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
    return {"name": name, "slug": slug, "template_key": template_key, "status": status, "components": components}, None


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
    return {
        "name": name,
        "block_name": block_name,
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
    return {
        "name": name,
        "component_key": component_key,
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
