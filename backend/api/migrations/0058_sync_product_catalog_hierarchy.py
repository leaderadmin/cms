from django.db import migrations


def sync_product_catalog_hierarchy(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    ProductGroup = apps.get_model("api", "ProductGroup")
    ProductType = apps.get_model("api", "ProductType")
    type_groups = {
        "card": ("the", "the-tin-dung", "thẻ tín dụng"),
        "loan": ("khoan-vay", "khoan-vay", "Khoản vay"),
        "saving": ("tiet-kiem", "tiet-kiem", "Tiết kiệm"),
        "service": ("dich-vu", "dich-vu", "Dịch vụ"),
        "promotion": ("uu-dai", "uu-dai", "Ưu đãi"),
    }
    types = {item.slug: item for item in ProductType.objects.all()}
    for source_kind, (type_slug, group_slug, group_name) in type_groups.items():
        product_type = types.get(type_slug)
        if product_type is None:
            continue
        ProductGroup.objects.update_or_create(
            slug=group_slug,
            defaults={"name": group_name, "product_type": product_type, "status": 1},
        )
        Product.objects.filter(kind=source_kind).update(kind=group_slug, product_type=product_type)


def reverse_sync_product_catalog_hierarchy(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    for source_kind, group_slug in {
        "card": "the-tin-dung",
        "loan": "khoan-vay",
        "saving": "tiet-kiem",
        "service": "dich-vu",
        "promotion": "uu-dai",
    }.items():
        Product.objects.filter(kind=group_slug).update(kind=source_kind)


class Migration(migrations.Migration):
    dependencies = [("api", "0057_product_legacy_id")]
    operations = [migrations.RunPython(sync_product_catalog_hierarchy, reverse_sync_product_catalog_hierarchy)]
