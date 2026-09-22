from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0016_systemsettings_domains")]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="avatar",
            field=models.FileField(blank=True, upload_to="users/avatars"),
        ),
    ]