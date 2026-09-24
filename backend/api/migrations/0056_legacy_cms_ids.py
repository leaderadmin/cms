from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0055_sync_cms_module_menu")]
    operations = [
        migrations.AddField("recruitmentregion", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField("recruitmentarea", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField("recruitmentjob", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField("faqcategory", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField("faqquestion", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField("dealer", "legacy_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
    ]