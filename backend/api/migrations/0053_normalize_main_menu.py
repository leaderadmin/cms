from django.db import migrations


def normalize_main_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    menu = apps.get_model("api", "Menu").objects.filter(slug="main").first()
    if not menu:
        return

    MenuItem.objects.filter(menu=menu, label="test").delete()

    media_items = list(MenuItem.objects.filter(menu=menu, view="media").order_by("id"))
    media = media_items[0] if media_items else None
    for duplicate in media_items[1:]:
        duplicate.delete()

    content = MenuItem.objects.filter(menu=menu, view="content").first() or MenuItem.objects.filter(menu=menu, label="Nội dung", parent__isnull=True).first()
    if content:
        content.label = "Nội dung"
        content.view = "content"
        content.href = "#content"
        content.parent = None
        content.sort_order = 7
        content.is_active = True
        content.save(update_fields=("label", "view", "href", "parent", "sort_order", "is_active"))

    if media and content:
        media.parent = content
        media.sort_order = 3
        media.required_permission = "media.read"
        media.is_active = True
        media.save(update_fields=("parent", "sort_order", "required_permission", "is_active"))

    entities = MenuItem.objects.filter(menu=menu, view="entities").order_by("id").first()
    if entities:
        entities.parent = None
        entities.href = "#entities"
        entities.sort_order = 5
        entities.is_active = True
        entities.save(update_fields=("parent", "href", "sort_order", "is_active"))

    root_order = {
        "overview": 0,
        "": 1,
        "access-management": 2,
        "monitoring": 3,
        "settings": 4,
        "entities": 5,
        "build-page": 6,
        "content": 7,
        "products": 8,
        "recruitment": 9,
        "faq": 10,
        "administration": 11,
    }
    for item in MenuItem.objects.filter(menu=menu, parent__isnull=True):
        if item.view in root_order:
            item.sort_order = root_order[item.view]
            item.save(update_fields=("sort_order",))


class Migration(migrations.Migration):
    dependencies = [("api", "0052_split_recruitment_faq_menu")]
    operations = [migrations.RunPython(normalize_main_menu, migrations.RunPython.noop)]
