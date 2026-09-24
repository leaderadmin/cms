from django.db import migrations


def finish_menu_cleanup(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(label="test").delete()
    order = {
        "Overview": 0,
        "Account": 1,
        "Access management": 2,
        "Monitoring": 3,
        "Settings": 4,
        "Entities": 5,
        "Build Page": 6,
        "Nội dung": 7,
        "Products": 8,
        "Recruitment": 9,
        "FAQs": 10,
        "Quản lý hành chính": 11,
    }
    for item in MenuItem.objects.filter(parent__isnull=True):
        if item.label in order:
            item.sort_order = order[item.label]
            item.save(update_fields=("sort_order",))


class Migration(migrations.Migration):
    dependencies = [("api", "0053_normalize_main_menu")]
    operations = [migrations.RunPython(finish_menu_cleanup, migrations.RunPython.noop)]
