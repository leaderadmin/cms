from django.db import migrations


def add_product_menu_item(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Main menu", "is_active": True})
    content, _ = MenuItem.objects.get_or_create(
        menu=menu,
        label="Nội dung",
        parent=None,
        defaults={"icon": "bi-collection", "sort_order": 5, "is_active": True},
    )
    item, _ = MenuItem.objects.get_or_create(menu=menu, view="products", defaults={"label": "Products"})
    item.label = "Products"
    item.href = "#products"
    item.icon = "bi-box-seam"
    item.required_permission = "product.read"
    item.parent = content
    item.sort_order = 5
    item.is_active = True
    item.save(update_fields=("label", "href", "icon", "required_permission", "parent", "sort_order", "is_active"))


def remove_product_menu_item(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="products").delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0031_product_models")]

    operations = [migrations.RunPython(add_product_menu_item, remove_product_menu_item)]
