from django.db import migrations


def complete_product_attribute_set(apps, schema_editor):
    ProductAttribute = apps.get_model("api", "ProductAttribute")
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")
    attribute_set = ProductAttributeSet.objects.filter(slug="thong-tin-san-pham").first()
    if attribute_set:
        attribute_set.attributes.set(ProductAttribute.objects.filter(status=1).order_by("ordering", "name", "id"))


def reverse_product_attribute_set(apps, schema_editor):
    ProductAttribute = apps.get_model("api", "ProductAttribute")
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")
    attribute_set = ProductAttributeSet.objects.filter(slug="thong-tin-san-pham").first()
    if attribute_set:
        attribute_set.attributes.set(ProductAttribute.objects.filter(slug__in=[
            "uu-dai-dac-biet-khac",
            "han-muc-giao-dich",
            "tinh-nang-noi-bat",
            "phi-thuong-nien",
            "lai-suat-nam",
        ]))


class Migration(migrations.Migration):
    dependencies = [("api", "0040_seed_product_groups")]
    operations = [migrations.RunPython(complete_product_attribute_set, reverse_product_attribute_set)]
