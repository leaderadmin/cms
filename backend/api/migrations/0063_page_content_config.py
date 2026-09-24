from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0062_page_short_codes_and_articles")]

    operations = [
        migrations.AddField(
            model_name="page",
            name="content_config",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]