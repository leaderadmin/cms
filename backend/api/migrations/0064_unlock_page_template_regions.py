from django.db import migrations


def unlock_template_regions(apps, schema_editor):
    PageTemplate = apps.get_model("api", "PageTemplate")
    for template in PageTemplate.objects.all():
        regions = template.regions or []
        changed = False
        for region in regions:
            if region.get("key", region.get("id")) in {"header", "footer"} and region.get("locked"):
                region["locked"] = False
                changed = True
        if changed:
            template.regions = regions
            template.save(update_fields=["regions", "updated_at"])


def relock_template_regions(apps, schema_editor):
    PageTemplate = apps.get_model("api", "PageTemplate")
    for template in PageTemplate.objects.all():
        regions = template.regions or []
        changed = False
        for region in regions:
            if region.get("key", region.get("id")) in {"header", "footer"} and not region.get("locked"):
                region["locked"] = True
                changed = True
        if changed:
            template.regions = regions
            template.save(update_fields=["regions", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [("api", "0063_page_content_config")]
    operations = [migrations.RunPython(unlock_template_regions, relock_template_regions)]
