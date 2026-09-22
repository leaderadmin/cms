from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("api", "0009_businessentity")]

    operations = [migrations.DeleteModel(name="BusinessEntity")]
