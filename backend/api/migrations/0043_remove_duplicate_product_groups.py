from django.db import migrations


DUPLICATE_GROUP_SLUGS = ("card", "loan", "saving", "service", "promotion")


def remove_duplicate_groups(apps, schema_editor):
    ProductGroup = apps.get_model("api", "ProductGroup")
    ProductGroup.objects.filter(slug__in=DUPLICATE_GROUP_SLUGS).delete()


def restore_duplicate_groups(apps, schema_editor):
    ProductGroup = apps.get_model("api", "ProductGroup")
    names = {
        "card": "Thẻ",
        "loan": "Khoản vay",
        "saving": "Tiết kiệm",
        "service": "Dịch vụ",
        "promotion": "Ưu đãi",
    }
    for ordering, slug in enumerate(DUPLICATE_GROUP_SLUGS):
        ProductGroup.objects.get_or_create(slug=slug, defaults={"name": names[slug], "status": 1, "ordering": ordering})


class Migration(migrations.Migration):
    dependencies = [("api", "0042_seed_attribute_sets_menu")]
    operations = [migrations.RunPython(remove_duplicate_groups, restore_duplicate_groups)]
