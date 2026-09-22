from django.db import migrations


def normalize_templates_and_pages(apps, schema_editor):
    Page = apps.get_model("api", "Page")
    PageTemplate = apps.get_model("api", "PageTemplate")
    PageVersion = apps.get_model("api", "PageVersion")

    for template in PageTemplate.objects.all():
        regions = []
        for index, region in enumerate(template.regions or []):
            regions.append({
                "id": region.get("id") or region.get("key") or f"region-{index + 1}",
                "locked": bool(region.get("locked", False)),
                "maxBlocks": region.get("maxBlocks", region.get("max_blocks")),
                "allowedBlocks": region.get("allowedBlocks", region.get("allowed_blocks", [])),
            })
        template.regions = regions
        template.save(update_fields=["regions"])

    for page in Page.objects.all():
        template = PageTemplate.objects.filter(key=page.template_key).first()
        if template:
            page.template = template
        regions = {}
        for component in page.components or []:
            region_id = component.get("key") or component.get("id")
            if region_id:
                regions[region_id] = component.get("modules", [])
        version = PageVersion.objects.create(page=page, regions=regions, version_number=1, created_by=page.created_by)
        page.draft_version = version
        if page.status == "published":
            page.published_version = version
        page.save(update_fields=["template", "draft_version", "published_version"])


class Migration(migrations.Migration):
    dependencies = [("api", "0027_page_versioning")]
    operations = [migrations.RunPython(normalize_templates_and_pages, migrations.RunPython.noop)]