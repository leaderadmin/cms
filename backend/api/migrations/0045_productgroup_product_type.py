from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("api", "0044_rename_product_sets_menu")]

    operations = [
        migrations.AddField(
            model_name="productgroup",
            name="product_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="groups",
                to="api.producttype",
            ),
        ),
    ]
