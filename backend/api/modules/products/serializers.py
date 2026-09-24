from django.utils.text import slugify

from ...models import Product, ProductAttribute, ProductAttributeSet, ProductCategory, ProductGroup, ProductTag, ProductTranslation, ProductType


def product_tags(product):
    legacy_tags = (product.extra_data or {}).get("tags", [])
    legacy_tags = [str(tag).strip() for tag in legacy_tags if str(tag).strip()] if isinstance(legacy_tags, list) else []
    managed_tags = list(product.managed_tags.values_list("name", flat=True))
    return list(dict.fromkeys(legacy_tags + managed_tags))


def serialize_product_tag(tag):
    return {"id": tag.id, "name": tag.name, "slug": tag.slug, "usage_count": tag.products.count()}


def serialize_product_item(item):
    translations = list(item.translations.all())
    translation = next((value for value in translations if value.language_code == "vi"), None) or (translations[0] if translations else None)
    return {"id": item.id, "name": item.name, "slug": item.slug, "title": translation.title if translation else item.name, "status": item.status, "status_label": item.get_status_display(), "tags": product_tags(item)}


def serialize_type(item, products_by_group=None):
    return {"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "ordering": item.ordering, "groups": [serialize_group(group, products_by_group) for group in item.groups.all()]}


def serialize_group(item, products_by_group=None):
    products = [serialize_product_item(product) for product in (products_by_group or {}).get(item.slug, [])]
    return {"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "ordering": item.ordering, "product_type_id": item.product_type_id, "products": products}


def serialize_category(item):
    return {"id": item.id, "name": item.name, "slug": item.slug, "parent_id": item.parent_id, "product_type_id": item.product_type_id, "status": item.status, "ordering": item.ordering}


def serialize_attribute(item):
    return {"id": item.id, "name": item.name, "slug": item.slug, "value_type": item.value_type, "status": item.status, "ordering": item.ordering}


def serialize_attribute_set(item):
    attributes = list(item.attributes.all())
    return {"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "ordering": item.ordering, "attribute_ids": [attribute.id for attribute in attributes], "attributes": [serialize_attribute(attribute) for attribute in attributes]}


def serialize_product(product, language_code=None):
    translations = list(product.translations.all())
    translation = next((item for item in translations if item.language_code == language_code), None) or (translations[0] if translations else None)
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "kind": product.kind,
        "status": product.status,
        "status_label": product.get_status_display(),
        "ordering": product.ordering,
        "is_featured": product.is_featured,
        "tags": product_tags(product),
        "tag_ids": list(product.managed_tags.values_list("id", flat=True)),
        "product_type": serialize_type(product.product_type) if product.product_type else None,
        "category": serialize_category(product.category) if product.category else None,
        "attribute_set": serialize_attribute_set(product.attribute_set) if product.attribute_set else None,
        "attributes": product.attributes or {},
        "extra_data": product.extra_data or {},
        "image": {"id": product.image_id, "name": product.image.original_name, "url": f"/api/media/{product.image_id}/download/"} if product.image else None,
        "start_date": product.start_date.isoformat() if product.start_date else None,
        "end_date": product.end_date.isoformat() if product.end_date else None,
        "translation": {
            "id": translation.id,
            "language_code": translation.language_code,
            "title": translation.title,
            "short_description": translation.short_description,
            "content": translation.content,
            "url_key": translation.url_key,
            "seo_title": translation.seo_title,
            "meta_keyword": translation.meta_keyword,
            "meta_description": translation.meta_description,
        } if translation else None,
        "translations": [{
            "id": item.id,
            "language_code": item.language_code,
            "title": item.title,
            "short_description": item.short_description,
            "content": item.content,
            "url_key": item.url_key,
            "seo_title": item.seo_title,
            "meta_keyword": item.meta_keyword,
            "meta_description": item.meta_description,
            "status": item.status,
        } for item in translations],
    }


def _translations_payload(data, status):
    translations = data.get("translations") or []
    primary = data.get("translation") or (translations[0] if translations else {})
    if not isinstance(primary, dict):
        return None, "Translation must be an object."
    language_code = str(primary.get("language_code") or "vi").strip().lower()
    title = str(primary.get("title") or "").strip()
    url_key = str(primary.get("url_key") or slugify(title)).strip()
    if not language_code or len(language_code) > 10 or not title or not url_key:
        return None, "A translation requires language, title and URL key."
    raw_items = [primary] + [item for item in translations if isinstance(item, dict) and item.get("language_code") != language_code]
    result = []
    seen = set()
    for item in raw_items:
        item_language = str(item.get("language_code") or "").strip().lower()
        item_title = str(item.get("title") or "").strip()
        item_url_key = str(item.get("url_key") or slugify(item_title)).strip()
        if not item_language or len(item_language) > 10 or not item_title or not item_url_key or item_language in seen:
            return None, "Each translation requires a unique language, title and URL key."
        seen.add(item_language)
        result.append({
            "language_code": item_language,
            "title": item_title[:255],
            "short_description": str(item.get("short_description") or ""),
            "content": str(item.get("content") or ""),
            "url_key": item_url_key[:280],
            "seo_title": str(item.get("seo_title") or "")[:255],
            "meta_keyword": str(item.get("meta_keyword") or "")[:255],
            "meta_description": str(item.get("meta_description") or ""),
            "status": status,
        })
    return result, None


def product_payload(data):
    name = str(data.get("name") or "").strip()
    slug = str(data.get("slug") or slugify(name)).strip()
    kind = str(data.get("kind") or "service").strip()
    if not name or not slug:
        return None, "Product name and slug are required."
    if not ProductGroup.objects.filter(slug=kind, status=1).exists():
        return None, "Invalid product group."
    try:
        status = int(data.get("status", Product.STATUS_DRAFT))
        ordering = int(data.get("ordering", 0) or 0)
        image_id = int(data["image_id"]) if data.get("image_id") else None
        product_type_id = int(data["product_type_id"]) if data.get("product_type_id") else None
        category_id = int(data["category_id"]) if data.get("category_id") else None
        attribute_set_id = int(data["attribute_set_id"]) if data.get("attribute_set_id") else None
    except (TypeError, ValueError):
        return None, "Product IDs, status and ordering must be valid numbers."
    if status not in {Product.STATUS_DRAFT, Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED}:
        return None, "Invalid product status."
    attributes = data.get("attributes") or {}
    extra_data = data.get("extra_data") or {}
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = tags.split(",")
    if not isinstance(attributes, dict) or not isinstance(extra_data, dict) or not isinstance(tags, list):
        return None, "Attributes and extra data must be objects."
    normalized_tags = []
    for tag in tags:
        value = str(tag).strip()
        if value and value not in normalized_tags:
            normalized_tags.append(value[:80])
    extra_data = {**extra_data, "tags": normalized_tags}
    try:
        tag_ids = [int(tag_id) for tag_id in data.get("tag_ids", [])]
    except (TypeError, ValueError):
        return None, "Tag IDs must be integers."
    translations, error = _translations_payload(data, status)
    if error:
        return None, error
    return {
        "name": name[:255], "slug": slug[:280], "kind": kind, "status": status, "ordering": ordering,
        "is_featured": bool(data.get("is_featured", False)), "image_id": image_id,
        "product_type_id": product_type_id, "category_id": category_id, "attribute_set_id": attribute_set_id,
        "attributes": attributes, "extra_data": extra_data, "tags": normalized_tags, "tag_ids": list(dict.fromkeys(tag_ids)), "translations": translations,
    }, None


def metadata_payload(data, model):
    name = str(data.get("name") or "").strip()
    slug = str(data.get("slug") or slugify(name)).strip()
    if not name or not slug:
        return None, "Name and slug are required."
    payload = {"name": name[:180], "slug": slug[:180], "status": int(data.get("status", 1) or 1), "ordering": int(data.get("ordering", 0) or 0)}
    if model is ProductAttribute:
        payload["value_type"] = str(data.get("value_type") or "text")[:30]
    if model is ProductCategory:
        payload["parent_id"] = int(data["parent_id"]) if data.get("parent_id") else None
        payload["product_type_id"] = int(data["product_type_id"]) if data.get("product_type_id") else None
    if model is ProductGroup:
        payload["product_type_id"] = int(data["product_type_id"]) if data.get("product_type_id") else None
    if model is ProductAttributeSet:
        payload["attribute_ids"] = [int(value) for value in data.get("attribute_ids", [])]
    return payload, None


def tag_payload(data, tag=None):
    name = str(data.get("name") or "").strip()
    slug = str(data.get("slug") or slugify(name)).strip()
    if not name or not slug:
        return None, "Tag name and slug are required."
    return {"name": name[:80], "slug": slug[:100]}, None
