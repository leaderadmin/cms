from django.db import migrations


def group_faq_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu = Menu.objects.filter(slug="main").first()
    if menu is None:
        return

    parent, _ = MenuItem.objects.get_or_create(menu=menu, view="faq")
    parent.label = "FAQ"
    parent.href = "#faq"
    parent.icon = "bi-question-circle"
    parent.required_permission = ""
    parent.parent = None
    parent.sort_order = 10
    parent.is_active = True
    parent.save()

    for view, label, icon, sort_order in (
        ("faq-categories", "FAQ categories", "bi-folder2-open", 0),
        ("faq-questions", "FAQ questions", "bi-chat-square-text", 1),
    ):
        item = MenuItem.objects.filter(menu=menu, view=view).first()
        if item is None:
            item = MenuItem.objects.create(menu=menu, view=view)
        item.label = label
        item.href = f"#{view}"
        item.icon = icon
        item.required_permission = "faq.read"
        item.parent = parent
        item.sort_order = sort_order
        item.is_active = True
        item.save()


class Migration(migrations.Migration):
    dependencies = [("api", "0059_split_faq_menu")]
    operations = [migrations.RunPython(group_faq_menu, migrations.RunPython.noop)]