from django.db import migrations


ATTRIBUTE_DEFINITIONS = (
    ("Ưu đãi đặc biệt khác", "uu-dai-dac-biet-khac"),
    ("Hạn mức giao dịch", "han-muc-giao-dich"),
    ("Tính năng nổi bật", "tinh-nang-noi-bat"),
    ("Phí thường niên", "phi-thuong-nien"),
    ("Lãi suất (năm)", "lai-suat-nam"),
)


def seed_product_attributes(apps, schema_editor):
    ProductAttribute = apps.get_model("api", "ProductAttribute")
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")

    attributes = []
    for ordering, (name, slug) in enumerate(ATTRIBUTE_DEFINITIONS):
        attribute, _ = ProductAttribute.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "value_type": "text", "status": 1, "ordering": ordering},
        )
        attributes.append(attribute)

    attribute_set, _ = ProductAttributeSet.objects.get_or_create(
        slug="thong-tin-san-pham",
        defaults={"name": "Thông tin sản phẩm", "status": 1, "ordering": 0},
    )
    attribute_set.attributes.set(attributes)


def remove_product_attributes(apps, schema_editor):
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")
    ProductAttribute = apps.get_model("api", "ProductAttribute")
    ProductAttributeSet.objects.filter(slug="thong-tin-san-pham").delete()
    ProductAttribute.objects.filter(slug__in=[slug for _, slug in ATTRIBUTE_DEFINITIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0035_rename_api_product_kind_6d1e6a_idx_api_product_kind_15170f_idx_and_more")]

    operations = [migrations.RunPython(seed_product_attributes, remove_product_attributes)]