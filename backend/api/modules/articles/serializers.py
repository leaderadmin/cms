from django.utils.text import slugify

from ...models import Article, ArticleCategory, Tag


def serialize_tag(tag):
    return {"id": tag.id, "name": tag.name, "slug": tag.slug, "usage_count": tag.articles.count()}


def tag_payload(data, existing=None):
    name = str(data.get("name") or (existing.name if existing else "")).strip()[:80]
    if not name:
        return None, "Tag name is required."
    slug = str(data.get("slug") or slugify(name)).strip()[:100]
    if not slug:
        return None, "Tag slug is required."
    return {"name": name, "slug": slug}, None


def serialize_category(category):
    translation = category.translations.order_by("language_code").first()
    return {
        "id": category.id,
        "legacy_id": category.legacy_id,
        "name": category.name,
        "type": category.category_type,
        "status": category.status,
        "parent_id": category.parent_id,
        "ordering": category.ordering,
        "title": translation.title if translation else category.name,
        "translation": {
            "language_code": translation.language_code,
            "title": translation.title,
            "description": translation.description,
            "url_key": translation.url_key,
            "meta_keyword": translation.meta_keyword,
            "meta_description": translation.meta_description,
        } if translation else None,
    }


def category_payload(data):
    name = str(data.get("name") or "").strip()
    if not name:
        return None, "Category name is required."
    try:
        status = int(data.get("status", Article.STATUS_APPROVED))
        if status not in {Article.STATUS_DELETED, Article.STATUS_APPROVED, Article.STATUS_PENDING}:
            raise ValueError
        ordering = int(data.get("ordering", 0) or 0)
    except (TypeError, ValueError):
        return None, "Invalid category status or ordering."
    parent_id = data.get("parent_id")
    if parent_id in (None, ""):
        parent_id = None
    else:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return None, "Parent category ID must be an integer."
    translation = data.get("translation") or {}
    language_code = str(translation.get("language_code") or "vi").strip().lower()
    if len(language_code) > 10:
        return None, "A valid language code is required."
    return {
        "name": name[:255],
        "category_type": str(data.get("type") or "article").strip()[:64] or "article",
        "status": status,
        "ordering": ordering,
        "parent_id": parent_id,
        "translation": {
            "language_code": language_code,
            "title": str(translation.get("title") or name).strip()[:255],
            "description": str(translation.get("description") or ""),
            "url_key": str(translation.get("url_key") or "").strip()[:255],
            "meta_keyword": str(translation.get("meta_keyword") or "").strip()[:255],
            "meta_description": str(translation.get("meta_description") or ""),
        },
    }, None


def serialize_article(article, language_code=None):
    translations = article.translations.all()
    translation = next((item for item in translations if item.language_code == language_code), None)
    translation = translation or next(iter(translations), None)
    return {
        "id": article.id,
        "legacy_id": article.legacy_id,
        "name": article.name,
        "type": article.article_type,
        "status": article.status,
        "status_label": article.get_status_display(),
        "view_count": article.view_count,
        "ordering": article.ordering,
        "show_home": article.show_home,
        "is_feature": article.is_feature,
        "public_date": article.public_date.isoformat() if article.public_date else None,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "categories": [serialize_category(category) for category in article.categories.all()],
        "tags": list(dict.fromkeys((article.tags or []) + list(article.managed_tags.values_list("name", flat=True)))),
        "tag_ids": list(article.managed_tags.values_list("id", flat=True)),
        "cta": {
            "label": article.cta_label,
            "url": article.cta_url,
            "phone": article.cta_phone,
        } if article.cta_label or article.cta_url or article.cta_phone else None,
        "image": {
            "id": article.image_id,
            "name": article.image.original_name,
            "url": f"/api/media/{article.image_id}/download/",
        } if article.image else None,
        "translation": {
            "id": translation.id,
            "legacy_id": translation.legacy_id,
            "language_code": translation.language_code,
            "title": translation.title,
            "sub_title": translation.sub_title,
            "content": translation.content,
            "short_description": translation.short_description,
            "url_key": translation.url_key,
            "status": translation.status,
            "public_date": translation.public_date.isoformat() if translation.public_date else None,
            "seo_title": translation.seo_title,
            "meta_description": translation.meta_description,
            "seo_name": translation.seo_name,
        } if translation else None,
        "translations": [
            {"id": item.id, "language_code": item.language_code, "title": item.title, "status": item.status}
            for item in translations
        ],
    }


def article_payload(data):
    translations = data.get("translations") or []
    if not isinstance(translations, list):
        return None, "Translations must be an array."
    translation = data.get("translation") or (translations[0] if translations else {})
    title = str(translation.get("title", "")).strip()
    language_code = str(translation.get("language_code", "vi")).strip().lower()
    url_key = str(translation.get("url_key", "")).strip()
    if not title:
        return None, "A translation title is required."
    if not language_code or len(language_code) > 10:
        return None, "A valid language code is required."
    if not url_key:
        return None, "A URL key is required."
    try:
        status = int(data.get("status", Article.STATUS_PENDING))
        if status not in {Article.STATUS_DELETED, Article.STATUS_APPROVED, Article.STATUS_PENDING}:
            raise ValueError
    except (TypeError, ValueError):
        return None, "Invalid article status."
    try:
        category_ids = [int(category_id) for category_id in data.get("category_ids", [])]
    except (TypeError, ValueError):
        return None, "Category IDs must be integers."
    if len(set(category_ids)) > 1:
        return None, "Only one category can be selected."
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        return None, "Tags must be an array."
    tags = list(dict.fromkeys(str(tag).strip()[:80] for tag in tags if str(tag).strip()))[:50]
    try:
        tag_ids = [int(tag_id) for tag_id in data.get("tag_ids", [])]
    except (TypeError, ValueError):
        return None, "Tag IDs must be integers."
    try:
        image_id = int(data["image_id"]) if data.get("image_id") else None
    except (TypeError, ValueError):
        return None, "Image ID must be an integer."
    cta = data.get("cta") or {}
    cta_label = str(cta.get("label") or "").strip()[:80]
    cta_url = str(cta.get("url") or "").strip()[:500]
    cta_phone = str(cta.get("phone") or "").strip()[:40]
    if cta_url and not (cta_url.startswith("http://") or cta_url.startswith("https://") or cta_url.startswith("/")):
        return None, "CTA URL must be a valid http(s) or internal URL."
    translation_items = [translation]
    for item in translations:
        if isinstance(item, dict) and item.get("language_code") != language_code:
            translation_items.append(item)
    parsed_translations = []
    for item in translation_items:
        item_language = str(item.get("language_code") or "").strip().lower()
        item_title = str(item.get("title") or "").strip()
        item_url_key = str(item.get("url_key") or "").strip()
        if not item_language or len(item_language) > 10 or not item_title or not item_url_key:
            return None, "Each translation requires a language, title and URL key."
        parsed_translations.append({
            "language_code": item_language,
            "title": item_title[:255],
            "raw_title": str(item.get("raw_title") or item_title)[:255],
            "sub_title": str(item.get("sub_title") or "")[:255],
            "content": str(item.get("content") or ""),
            "short_description": str(item.get("short_description") or ""),
            "status": status,
            "url_key": item_url_key[:255],
            "seo_title": str(item.get("seo_title") or "")[:255],
            "seo_name": str(item.get("seo_name") or "")[:255],
            "meta_description": str(item.get("meta_description") or ""),
        })
    return {
        "name": str(data.get("name") or title).strip()[:255],
        "article_type": str(data.get("type") or "article").strip()[:64],
        "status": status,
        "ordering": int(data.get("ordering", 0) or 0),
        "show_home": bool(data.get("show_home", False)),
        "is_feature": bool(data.get("is_feature", False)),
        "translation": {
            "language_code": language_code,
            "title": title[:255],
            "raw_title": str(translation.get("raw_title") or title)[:255],
            "sub_title": str(translation.get("sub_title") or "")[:255],
            "content": str(translation.get("content") or ""),
            "short_description": str(translation.get("short_description") or ""),
            "status": status,
            "url_key": url_key[:255],
            "seo_title": str(translation.get("seo_title") or "")[:255],
            "seo_name": str(translation.get("seo_name") or "")[:255],
            "meta_description": str(translation.get("meta_description") or ""),
        },
        "translations": parsed_translations,
        "category_ids": category_ids,
        "tags": tags,
        "tag_ids": list(dict.fromkeys(tag_ids)),
        "image_id": image_id,
        "cta": {"label": cta_label, "url": cta_url, "phone": cta_phone},
    }, None