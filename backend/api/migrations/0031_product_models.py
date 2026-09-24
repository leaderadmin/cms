from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0030_pagecomponentdefinition"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("value_type", models.CharField(default="text", max_length=30)),
                ("status", models.SmallIntegerField(default=1)),
                ("ordering", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("ordering", "name", "id")},
        ),
        migrations.CreateModel(
            name="ProductType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("status", models.SmallIntegerField(default=1)),
                ("ordering", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("ordering", "name", "id")},
        ),
        migrations.CreateModel(
            name="ProductAttributeSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, unique=True)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("ordering", models.IntegerField(default=0)),
                ("status", models.SmallIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("attributes", models.ManyToManyField(blank=True, related_name="attribute_sets", to="api.productattribute")),
            ],
            options={"ordering": ("ordering", "name", "id")},
        ),
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("status", models.SmallIntegerField(default=1)),
                ("ordering", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="children", to="api.productcategory")),
                ("product_type", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="categories", to="api.producttype")),
            ],
            options={"ordering": ("ordering", "name", "id")},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=280, unique=True)),
                ("kind", models.CharField(choices=[("card", "Card"), ("loan", "Loan"), ("saving", "Saving"), ("service", "Service"), ("promotion", "Promotion")], default="service", max_length=30)),
                ("status", models.SmallIntegerField(choices=[(0, "Draft"), (1, "Active"), (-1, "Archived")], default=0)),
                ("ordering", models.IntegerField(default=0)),
                ("is_featured", models.BooleanField(default=False)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("attribute_set", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="api.productattributeset")),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="api.productcategory")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to=settings.AUTH_USER_MODEL)),
                ("image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="api.mediafile")),
                ("product_type", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="api.producttype")),
            ],
            options={"ordering": ("ordering", "-updated_at", "-id")},
        ),
        migrations.CreateModel(
            name="ProductTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(max_length=10)),
                ("title", models.CharField(max_length=255)),
                ("short_description", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("url_key", models.CharField(max_length=280)),
                ("seo_title", models.CharField(blank=True, max_length=255)),
                ("meta_keyword", models.CharField(blank=True, max_length=255)),
                ("meta_description", models.TextField(blank=True)),
                ("status", models.SmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="translations", to="api.product")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("product", "language_code"), name="unique_product_language")]},
        ),
        migrations.AddIndex(model_name="product", index=models.Index(fields=["kind", "status"], name="api_product_kind_6d1e6a_idx")),
        migrations.AddIndex(model_name="product", index=models.Index(fields=["category", "status"], name="api_product_categ_1c0b24_idx")),
        migrations.AddIndex(model_name="producttranslation", index=models.Index(fields=["language_code", "status"], name="api_productt_langua_0f1a4d_idx")),
        migrations.AddIndex(model_name="producttranslation", index=models.Index(fields=["url_key", "language_code"], name="api_productt_url_key_9f6c77_idx")),
    ]
