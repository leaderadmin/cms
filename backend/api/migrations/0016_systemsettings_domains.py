from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0015_systemsettings_logo_file")]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="api_domain",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="backoffice_domain",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]