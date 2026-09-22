from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0028_backfill_page_versions")]

    operations = [
        migrations.CreateModel(
            name="PageComponent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("block_name", models.SlugField(max_length=120, unique=True)),
                ("html", models.TextField(blank=True)),
                ("css", models.TextField(blank=True)),
                ("js", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="published", max_length=20)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("name", "id")},
        ),
    ]