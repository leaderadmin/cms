from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_article_legacy_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
