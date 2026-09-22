from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("api", "0026_seed_page_templates")]

    operations = [
        migrations.AddField(
            model_name="page",
            name="template",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pages", to="api.pagetemplate"),
        ),
        migrations.CreateModel(
            name="PageVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("regions", models.JSONField(blank=True, default=dict)),
                ("version_number", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="page_versions", to="auth.user")),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="api.page")),
            ],
            options={"ordering": ("-version_number", "-id")},
        ),
        migrations.AddConstraint(
            model_name="pageversion",
            constraint=models.UniqueConstraint(fields=("page", "version_number"), name="unique_page_version_number"),
        ),
        migrations.AddField(
            model_name="page",
            name="draft_version",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="draft_pages", to="api.pageversion"),
        ),
        migrations.AddField(
            model_name="page",
            name="published_version",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="published_pages", to="api.pageversion"),
        ),
    ]