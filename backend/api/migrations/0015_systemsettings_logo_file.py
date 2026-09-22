from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0014_systemsettings")]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="logo_file",
            field=models.FileField(blank=True, upload_to="system/branding"),
        ),
    ]
