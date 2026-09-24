from django.db import migrations


def split_faq_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu = Menu.objects.filter(slug="main").first()
    if menu is None:
        return

    faq = MenuItem.objects.filter(menu=menu, view="faq").order_by("id").first()
    if faq is None:
        faq = MenuItem.objects.create(menu=menu, view="faq-questions")
    faq.label = "FAQ questions"
    faq.href = "#faq-questions"
    faq.view = "faq-questions"
    faq.icon = "bi-question-circle"
    faq.required_permission = "faq.read"
    faq.parent = None
    faq.sort_order = 11
    faq.is_active = True
    faq.save()

    category = MenuItem.objects.filter(menu=menu, view="faq-categories").first()
    if category is None:
        category = MenuItem.objects.create(menu=menu, view="faq-categories")
    category.label = "FAQ categories"
    category.href = "#faq-categories"
    category.icon = "bi-folder2-open"
    category.required_permission = "faq.read"
    category.parent = None
    category.sort_order = 10
    category.is_active = True
    category.save()


def reverse_split_faq_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="faq-categories").delete()
    item = MenuItem.objects.filter(view="faq-questions").first()
    if item:
        item.label = "FAQs"
        item.href = "#faq"
        item.view = "faq"
        item.save(update_fields=("label", "href", "view"))


class Migration(migrations.Migration):
    dependencies = [("api", "0058_sync_product_catalog_hierarchy")]
    operations = [migrations.RunPython(split_faq_menu, reverse_split_faq_menu)]
