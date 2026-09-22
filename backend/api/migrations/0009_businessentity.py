from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0008_userprofile")]

    operations = [
        migrations.CreateModel(
            name="BusinessEntity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=120, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("entity_type", models.CharField(db_index=True, max_length=80)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("entity_type", "name")},
        ),
    ]