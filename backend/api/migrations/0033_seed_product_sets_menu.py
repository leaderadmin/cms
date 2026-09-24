from django.db import migrations


def add_product_sets_menu_item(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Main menu", "is_active": True})
    content, _ = MenuItem.objects.get_or_create(
        menu=menu,
        label="Nội dung",
        parent=None,
        defaults={"icon": "bi-collection", "sort_order": 5, "is_active": True},
    )
    product, _ = MenuItem.objects.get_or_create(menu=menu, view="products", defaults={"label": "Products"})
    product.label = "Products"
    product.href = "#products"
    product.icon = "bi-box-seam"
    product.required_permission = "product.read"
    product.parent = None
    product.sort_order = 6
    product.is_active = True
    product.save(update_fields=("label", "href", "icon", "required_permission", "parent", "sort_order", "is_active"))
    item, _ = MenuItem.objects.get_or_create(menu=menu, view="product-sets", defaults={"label": "Product sets"})
    item.label = "Product sets"
    item.href = "#product-sets"
    item.icon = "bi-collection"
    item.required_permission = "product.read"
    item.parent = product
    item.sort_order = 0
    item.is_active = True
    item.save(update_fields=("label", "href", "icon", "required_permission", "parent", "sort_order", "is_active"))


def remove_product_sets_menu_item(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="product-sets").delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0032_seed_product_menu")]

    operations = [migrations.RunPython(add_product_sets_menu_item, remove_product_sets_menu_item)]