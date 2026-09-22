from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("api", "0012_mediafile")]

    operations = [
        migrations.CreateModel(
            name="MediaFolder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="media_folders", to=settings.AUTH_USER_MODEL)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="api.mediafolder")),
            ],
            options={"ordering": ("name",), "constraints": [models.UniqueConstraint(fields=("parent", "name"), name="unique_media_folder_name")]},
        ),
        migrations.AddField(
            model_name="mediafile",
            name="folder",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="files", to="api.mediafolder"),
        ),
    ]
