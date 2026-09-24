from django.db import migrations


def rename_product_structure_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="product-sets").update(label="Catalog structure")


def restore_product_structure_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="product-sets").update(label="Product sets")


class Migration(migrations.Migration):
    dependencies = [("api", "0043_remove_duplicate_product_groups")]

    operations = [migrations.RunPython(rename_product_structure_menu, restore_product_structure_menu)]
