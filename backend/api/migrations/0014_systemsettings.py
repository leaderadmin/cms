from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0013_mediafolder_mediafile_folder")]

    operations = [
        migrations.CreateModel(
            name="SystemSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("system_name", models.CharField(default="Startup Backoffice", max_length=160)),
                ("logo_url", models.URLField(blank=True, max_length=500)),
                ("favicon_url", models.URLField(blank=True, max_length=500)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("website_url", models.URLField(blank=True, max_length=500)),
                ("support_email", models.EmailField(blank=True, max_length=254)),
                ("version", models.CharField(default="1.0.0", max_length=40)),
                ("footer_text", models.CharField(default="operations console", max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
