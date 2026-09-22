from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0024_tag_article_managed_tags")]

    operations = [
        migrations.CreateModel(
            name="PageTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("key", models.SlugField(max_length=120, unique=True)),
                ("regions", models.JSONField(blank=True, default=list)),
                ("tokens", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="published", max_length=20)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("name", "id")},
        ),
    ]