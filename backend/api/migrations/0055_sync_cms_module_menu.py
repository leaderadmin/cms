from django.db import migrations


def sync_cms_module_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(
        slug="main",
        defaults={"name": "Main menu", "is_active": True},
    )

    def item(view, label, href, icon, permission, parent=None, sort_order=0):
        current = MenuItem.objects.filter(menu=menu, view=view).order_by("id").first()
        if current is None:
            current = MenuItem.objects.create(menu=menu, view=view)
        current.label = label
        current.href = href
        current.icon = icon
        current.required_permission = permission
        current.parent = parent
        current.sort_order = sort_order
        current.is_active = True
        current.save(update_fields=(
            "label", "href", "icon", "required_permission", "parent", "sort_order", "is_active"
        ))
        return current

    products = item("products", "Products", "#products", "bi-box-seam", "product.read", sort_order=8)
    item("product-sets", "Catalog structure", "#product-sets", "bi-collection", "product.read", products, 0)
    item("attribute-sets", "Attribute sets", "#attribute-sets", "bi-sliders", "product.read", products, 1)
    item("product-tags", "Product tags", "#product-tags", "bi-tags", "product.tag.read", products, 2)

    item("recruitment", "Recruitment", "#recruitment", "bi-briefcase", "recruitment.read", sort_order=9)
    item("faq", "FAQs", "#faq", "bi-question-circle", "faq.read", sort_order=10)

    administration = item(
        "administration",
        "Quản lý hành chính",
        "#administration",
        "bi-diagram-3",
        "",
        sort_order=11,
    )
    item("admin-regions", "Miền", "#admin-regions", "bi-globe2", "recruitment.department.read", administration, 0)
    item("admin-areas", "Khu vực", "#admin-areas", "bi-map", "recruitment.department.read", administration, 1)
    item("dealers", "Đơn vị kinh doanh", "#dealers", "bi-building", "dealer.read", administration, 2)


class Migration(migrations.Migration):
    dependencies = [("api", "0054_finish_menu_cleanup")]
    operations = [migrations.RunPython(sync_cms_module_menu, migrations.RunPython.noop)]
