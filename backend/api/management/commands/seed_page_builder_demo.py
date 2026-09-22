from django.core.management.base import BaseCommand

from api.models import Page, PageTemplate


class Command(BaseCommand):
    help = "Create a page-builder demo template and page for drag-and-drop testing."

    def handle(self, *args, **options):
        template, _ = PageTemplate.objects.update_or_create(
            key="demo-builder",
            defaults={
                "name": "Demo page builder",
                "status": "published",
                "regions": [
                    {"id": "header", "label": "Header", "locked": False, "maxBlocks": 2, "allowedBlocks": ["demo-header"]},
                    {"id": "main", "label": "Main content", "locked": False, "maxBlocks": None, "allowedBlocks": ["demo-header"]},
                    {"id": "footer", "label": "Footer", "locked": False, "maxBlocks": 2, "allowedBlocks": ["demo-header"]},
                ],
                "tokens": {"primary_color": "#0C447C", "radius": "8px", "font": "Inter"},
            },
        )
        page, _ = Page.objects.update_or_create(
            slug="demo-drag-drop",
            defaults={"name": "Demo kéo thả block", "template": template, "template_key": template.key, "status": "draft", "components": []},
        )
        self.stdout.write(self.style.SUCCESS(f"Page builder demo is ready: {page.slug}"))
