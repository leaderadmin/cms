from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0061_dealer_types")]

    operations = [
        migrations.AddField(model_name="page", name="short_code", field=models.SlugField(blank=True, max_length=120, null=True, unique=True)),
        migrations.AddField(model_name="page", name="article_ids", field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name="pagecomponent", name="short_code", field=models.SlugField(blank=True, max_length=120, null=True, unique=True)),
        migrations.AddField(model_name="pagecomponentdefinition", name="short_code", field=models.SlugField(blank=True, max_length=120, null=True, unique=True)),
    ]