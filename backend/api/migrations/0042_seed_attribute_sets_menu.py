from django.db import migrations


def add_attribute_sets_menu_item(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Main menu", "is_active": True})
    products = MenuItem.objects.filter(menu=menu, view="products").order_by("id").first()
    if not products:
        products = MenuItem.objects.create(
            menu=menu,
            label="Products",
            href="#products",
            view="products",
            icon="bi-box-seam",
            required_permission="product.read",
            sort_order=6,
            is_active=True,
        )
    item, _ = MenuItem.objects.get_or_create(menu=menu, view="attribute-sets", defaults={"label": "Attribute sets"})
    item.label = "Attribute sets"
    item.href = "#attribute-sets"
    item.icon = "bi-ui-checks-grid"
    item.required_permission = "product.read"
    item.parent = products
    item.sort_order = 1
    item.is_active = True
    item.save(update_fields=("label", "href", "icon", "required_permission", "parent", "sort_order", "is_active"))


def remove_attribute_sets_menu_item(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="attribute-sets").delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0041_complete_product_attribute_set")]
    operations = [migrations.RunPython(add_attribute_sets_menu_item, remove_attribute_sets_menu_item)]
