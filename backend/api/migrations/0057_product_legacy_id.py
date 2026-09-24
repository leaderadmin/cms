from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0056_legacy_cms_ids")]
    operations = [
        migrations.AddField("product", "legacy_id", models.CharField(blank=True, max_length=40, null=True, unique=True)),
    ]