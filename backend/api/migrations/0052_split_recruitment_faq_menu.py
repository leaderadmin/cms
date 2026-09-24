from django.db import migrations


def split_recruitment_faq_menu(apps, schema_editor):
    MenuItem = apps.get_model("api", "MenuItem")
    MenuItem.objects.filter(view="recruitment-departments").delete()
    for view, label, href, permission, sort_order, icon in (
        ("recruitment", "Recruitment", "#recruitment", "recruitment.read", 6, "bi-briefcase"),
        ("faq", "FAQs", "#faq", "faq.read", 7, "bi-question-circle"),
    ):
        item = MenuItem.objects.filter(view=view).order_by("id").first()
        if not item:
            continue
        item.label = label
        item.href = href
        item.parent = None
        item.required_permission = permission
        item.sort_order = sort_order
        item.icon = icon
        item.is_active = True
        item.save(update_fields=("label", "href", "parent", "required_permission", "sort_order", "icon", "is_active"))


class Migration(migrations.Migration):
    dependencies = [("api", "0051_seed_administration_menu")]
    operations = [migrations.RunPython(split_recruitment_faq_menu, migrations.RunPython.noop)]
