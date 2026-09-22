from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_article_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='cta_label',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='article',
            name='cta_phone',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='article',
            name='cta_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]