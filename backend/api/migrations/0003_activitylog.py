from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0002_authsession"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(max_length=10)),
                ("path", models.CharField(max_length=255)),
                ("status_code", models.PositiveSmallIntegerField()),
                ("duration_ms", models.PositiveIntegerField(default=0)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activity_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=["-created_at"], name="api_activit_created_011954_idx"),
                    models.Index(fields=["user", "-created_at"], name="api_activit_user_id_29f0f8_idx"),
                    models.Index(fields=["path", "-created_at"], name="api_activit_path_9a3dc8_idx"),
                ],
            },
        ),
    ]