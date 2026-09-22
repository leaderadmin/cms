import hashlib
import json
from copy import deepcopy
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache

from ...models import Article

CACHE_SECONDS = 60


def _cache_key(source):
    encoded = json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"page-content:{digest}"


def _article_items(source):
    queryset = Article.objects.filter(status=Article.STATUS_APPROVED)
    filters = source.get("filter") or {}
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
        items = _article_items(source) if source.get("collection") else _external_items(source)
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
