from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0029_pagecomponent")]

    operations = [
        migrations.CreateModel(
            name="PageComponentDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("component_key", models.SlugField(max_length=120, unique=True)),
                ("prehtml", models.TextField(blank=True)),
                ("html", models.TextField(blank=True)),
                ("css", models.TextField(blank=True)),
                ("js", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("backhtml", models.TextField(blank=True)),
                ("blocks", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="published", max_length=20)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("name", "id")},
        ),
    ]
