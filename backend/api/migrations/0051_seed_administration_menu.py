from django.db import migrations


def seed_administration_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Main menu", "is_active": True})
    administration, _ = MenuItem.objects.get_or_create(menu=menu, view="administration", defaults={"label": "Quản lý hành chính"})
    administration.label = "Quản lý hành chính"
    administration.href = "#administration"
    administration.icon = "bi-diagram-3"
    administration.parent = None
    administration.sort_order = 5
    administration.is_active = True
    administration.save()
    children = (
        ("admin-regions", "Miền", "#admin-regions", 0),
        ("admin-areas", "Khu vực", "#admin-areas", 1),
        ("dealers", "Đơn vị kinh doanh", "#dealers", 2),
    )
    for view, label, href, sort_order in children:
        item, _ = MenuItem.objects.get_or_create(menu=menu, view=view, defaults={"label": label})
        item.label = label
        item.href = href
        item.parent = administration
        item.sort_order = sort_order
        item.is_active = True
        item.required_permission = "dealer.read" if view == "dealers" else "recruitment.department.read"
        item.save()


class Migration(migrations.Migration):
    dependencies = [("api", "0050_recruitment_location_hierarchy")]
    operations = [migrations.RunPython(seed_administration_menu, migrations.RunPython.noop)]
