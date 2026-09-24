from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0065_dynamicform"),
    ]

    operations = [
        migrations.AddField(
            model_name="dynamicform",
            name="submit_url",
            field=models.URLField(blank=True),
        ),
    ]
