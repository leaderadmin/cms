import hashlib
import json
from copy import deepcopy
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache

from ...models import Article, Page, Product

CACHE_SECONDS = 60


def _cache_key(source):
    encoded = json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"page-content:{digest}"


def _article_items(source):
    queryset = Article.objects.filter(status=Article.STATUS_APPROVED)
    filters = source.get("filter") or {}
    article_ids = filters.get("ids")
    if isinstance(article_ids, list):
        valid_ids = [int(article_id) for article_id in article_ids if str(article_id).isdigit()]
        queryset = queryset.filter(id__in=valid_ids)
    category_id = filters.get("category_id")
    if category_id not in (None, "") and str(category_id).isdigit():
        queryset = queryset.filter(categories__id=int(category_id))
    for field, value in filters.items():
        if field in {"article_type", "show_home", "is_feature"}:
            queryset = queryset.filter(**{field: value})
    try:
        limit = min(max(int(source.get("limit", 10)), 0), 100)
    except (TypeError, ValueError):
        limit = 10
    items = []
    for article in queryset.select_related("image").prefetch_related("translations")[:limit]:
        translation = article.translations.filter(language_code="vi").first() or article.translations.first()
        image_url = None
        if article.image and article.image.file:
            try:
                image_url = article.image.file.url
            except ValueError:
                image_url = None
        items.append({
            "id": article.id,
            "title": translation.title if translation else article.name,
            "slug": translation.url_key if translation else str(article.id),
            "description": translation.short_description if translation else "",
            "image": image_url,
            "public_date": article.public_date.isoformat() if article.public_date else None,
        })
    return items


def _page_items(source):
    queryset = Page.objects.filter(status=Page.STATUS_PUBLISHED)
    filters = source.get("filter") or {}
    page_ids = filters.get("ids")
    if isinstance(page_ids, list):
        valid_ids = [int(page_id) for page_id in page_ids if str(page_id).isdigit()]
        queryset = queryset.filter(id__in=valid_ids)
    template_key = filters.get("template_key")
    if template_key:
        queryset = queryset.filter(template_key=str(template_key))
    try:
        limit = min(max(int(source.get("limit", 10)), 0), 100)
    except (TypeError, ValueError):
        limit = 10
    return [
        {
            "id": page.id,
            "title": page.name,
            "name": page.name,
            "slug": page.slug,
            "url": f"/{page.slug}",
            "template_key": page.template_key,
            "status": page.status,
        }
        for page in queryset.order_by("name", "id")[:limit]
    ]


def _product_items(source):
    queryset = Product.objects.filter(status=Product.STATUS_ACTIVE).select_related("product_type", "category", "image").prefetch_related("translations")
    filters = source.get("filter") or {}
    product_ids = filters.get("ids")
    if isinstance(product_ids, list):
        valid_ids = [int(product_id) for product_id in product_ids if str(product_id).isdigit()]
        queryset = queryset.filter(id__in=valid_ids)
    for field in ("kind", "product_type_id", "category_id", "is_featured"):
        if field in filters and filters[field] not in (None, ""):
            queryset = queryset.filter(**{field: filters[field]})
    try:
        limit = min(max(int(source.get("limit", 10)), 0), 100)
    except (TypeError, ValueError):
        limit = 10
    items = []
    for product in queryset.order_by("ordering", "name", "id")[:limit]:
        translation = product.translations.filter(language_code="vi", status=Product.STATUS_ACTIVE).first() or product.translations.filter(status=Product.STATUS_ACTIVE).first()
        presentation = (product.extra_data or {}).get("presentation") or {}
        items.append({
            "id": product.id,
            "title": translation.title if translation else product.name,
            "name": product.name,
            "slug": product.slug,
            "url": f"/products/{product.slug}",
            "kind": product.kind,
            "description": translation.short_description if translation else "",
            "image": product.image.file.url if product.image and product.image.file else None,
            "is_featured": product.is_featured,
            "attributes": product.attributes or {},
            "template_key": presentation.get("template_key") or "product-detail",
            "display_variant": presentation.get("display_variant") or "standard",
            "show_attributes": presentation.get("show_attributes", True),
        })
    return items


def _external_items(source):
    api = str(source.get("api") or "").strip()
    if not api.startswith(("http://", "https://")):
        return []
    params = source.get("params") or {}
    query = urlencode({str(key): str(value) for key, value in params.items()})
    url = f"{api}?{query}" if query else api
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, TypeError):
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "results", "data"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def resolve_source(source, limit=None):
    if not isinstance(source, dict):
        return []
    source = deepcopy(source)
    if limit is not None:
        source["limit"] = limit
    key = _cache_key(source)
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        collection = source.get("collection")
        items = _article_items(source) if collection == "articles" else _page_items(source) if collection == "pages" else _product_items(source) if collection == "products" else _external_items(source)
    except (TypeError, ValueError):
        items = []
    try:
        limit = source.get("limit")
        if limit is not None:
            items = items[: max(0, min(int(limit), 100))]
    except (TypeError, ValueError):
        items = items[:10]
    cache.set(key, items, CACHE_SECONDS)
    return items


def resolve_content(block, limit=None):
    resolved = deepcopy(block) if isinstance(block, dict) else {"type": "", "props": {}}
    props = resolved.setdefault("props", {})
    source = props.get("source")
    if isinstance(source, dict):
        props["items"] = resolve_source(source, limit=limit)
    return resolved
