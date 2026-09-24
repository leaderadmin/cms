from django.db import migrations


def split_products_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    products = MenuItem.objects.filter(view="products").order_by("id").first()
    if not products:
        return
    products.parent = None
    products.sort_order = 6
    products.save(update_fields=("parent", "sort_order"))
    product_sets = MenuItem.objects.filter(view="product-sets").order_by("id").first()
    if product_sets:
        product_sets.parent = products
        product_sets.sort_order = 0
        product_sets.save(update_fields=("parent", "sort_order"))


def restore_products_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    content = MenuItem.objects.filter(label="Nội dung", parent__isnull=True).order_by("id").first()
    products = MenuItem.objects.filter(view="products").order_by("id").first()
    if products and content:
        products.parent = content
        products.sort_order = 5
        products.save(update_fields=("parent", "sort_order"))
    product_sets = MenuItem.objects.filter(view="product-sets").order_by("id").first()
    if product_sets and content:
        product_sets.parent = content
        product_sets.sort_order = 6
        product_sets.save(update_fields=("parent", "sort_order"))


class Migration(migrations.Migration):
    dependencies = [("api", "0033_seed_product_sets_menu")]

    operations = [migrations.RunPython(split_products_menu, restore_products_menu)]