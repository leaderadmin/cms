from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def migrate_product_tags(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    ProductTag = apps.get_model("api", "ProductTag")
    for product in Product.objects.all():
        extra_data = product.extra_data or {}
        for value in extra_data.get("tags", []) if isinstance(extra_data, dict) else []:
            name = str(value).strip()
            if not name:
                continue
            tag, _ = ProductTag.objects.get_or_create(name=name[:80], defaults={"slug": slugify(name)[:100]})
            product.managed_tags.add(tag)


class Migration(migrations.Migration):
    dependencies = [("api", "0045_productgroup_product_type")]
    operations = [
        migrations.CreateModel(
            name="ProductTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.AddField(
            model_name="product",
            name="managed_tags",
            field=models.ManyToManyField(blank=True, related_name="products", to="api.producttag"),
        ),
        migrations.RunPython(migrate_product_tags, migrations.RunPython.noop),
    ]