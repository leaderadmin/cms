from django.db import migrations


TEMPLATES = [
    {
        "name": "Trang chủ",
        "key": "home",
        "regions": [
            {"key": "header", "label": "header", "locked": True, "max_blocks": 1, "allowed_blocks": []},
            {"key": "hero", "label": "hero", "locked": False, "max_blocks": 1, "allowed_blocks": ["hero-slider", "hero-static"]},
            {"key": "main", "label": "main", "locked": False, "max_blocks": None, "allowed_blocks": ["quick-links", "product-cards", "exchange-rate-table", "news-list", "cta-banner"]},
            {"key": "footer", "label": "footer", "locked": True, "max_blocks": 1, "allowed_blocks": []},
        ],
    },
    {
        "name": "Trang sản phẩm",
        "key": "product",
        "regions": [
            {"key": "header", "label": "header", "locked": True, "max_blocks": 1, "allowed_blocks": []},
            {"key": "main", "label": "main", "locked": False, "max_blocks": None, "allowed_blocks": ["product-cards", "exchange-rate-table", "cta-banner"]},
            {"key": "footer", "label": "footer", "locked": True, "max_blocks": 1, "allowed_blocks": []},
        ],
    },
    {
        "name": "Tin tức chi tiết",
        "key": "article-detail",
        "regions": [
            {"key": "header", "label": "header", "locked": True, "max_blocks": 1, "allowed_blocks": []},
            {"key": "main", "label": "main", "locked": False, "max_blocks": None, "allowed_blocks": ["news-list", "cta-banner"]},
            {"key": "footer", "label": "footer", "locked": True, "max_blocks": 1, "allowed_blocks": []},
        ],
    },
    {
        "name": "Landing khuyến mãi",
        "key": "promotion-landing",
        "regions": [
            {"key": "header", "label": "header", "locked": True, "max_blocks": 1, "allowed_blocks": []},
            {"key": "hero", "label": "hero", "locked": False, "max_blocks": 1, "allowed_blocks": ["hero-static"]},
            {"key": "main", "label": "main", "locked": False, "max_blocks": None, "allowed_blocks": ["quick-links", "product-cards", "cta-banner"]},
            {"key": "footer", "label": "footer", "locked": True, "max_blocks": 1, "allowed_blocks": []},
        ],
    },
]


def seed_templates(apps, schema_editor):
    PageTemplate = apps.get_model("api", "PageTemplate")
    for item in TEMPLATES:
        PageTemplate.objects.get_or_create(
            key=item["key"],
            defaults={"name": item["name"], "regions": item["regions"], "tokens": {"primary_color": "#0C447C", "radius": "8px", "font": "Inter"}, "status": "published"},
        )


def remove_templates(apps, schema_editor):
    apps.get_model("api", "PageTemplate").objects.filter(key__in=[item["key"] for item in TEMPLATES]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0025_pagetemplate")]
    operations = [migrations.RunPython(seed_templates, remove_templates)]
