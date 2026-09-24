from django.db import migrations


GROUPS = (
    ("Thẻ", "card", 0),
    ("Khoản vay", "loan", 1),
    ("Tiết kiệm", "saving", 2),
    ("Dịch vụ", "service", 3),
    ("Ưu đãi", "promotion", 4),
)


def seed_product_groups(apps, schema_editor):
    ProductGroup = apps.get_model("api", "ProductGroup")
    for name, slug, ordering in GROUPS:
        ProductGroup.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "status": 1, "ordering": ordering},
        )


def remove_product_groups(apps, schema_editor):
    ProductGroup = apps.get_model("api", "ProductGroup")
    ProductGroup.objects.filter(slug__in=[slug for _, slug, _ in GROUPS]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0039_productgroup_alter_product_kind")]

    operations = [migrations.RunPython(seed_product_groups, remove_product_groups)]