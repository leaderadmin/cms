from django.core.management.base import BaseCommand

from api.models import PageComponent, PageComponentDefinition


class Command(BaseCommand):
    help = "Create reusable blocks and a composite component for drag-and-drop testing."

    def handle(self, *args, **options):
        blocks = [
            {
                "name": "Demo logo",
                "block_name": "demo-logo",
                "html": '<a class="demo-logo" href="#">STARTUP CMS</a>',
                "css": ".demo-logo { color: #0c447c; font-weight: 700; text-decoration: none; }",
                "content": '{"label":"STARTUP CMS"}',
            },
            {
                "name": "Demo menu",
                "block_name": "demo-menu",
                "html": '<nav class="demo-menu"><a href="#">Trang chủ</a><a href="#">Sản phẩm</a><a href="#">Liên hệ</a></nav>',
                "css": ".demo-menu { display: flex; gap: 16px; } .demo-menu a { color: #2c2c2a; text-decoration: none; }",
                "content": '{"items":["Trang chủ","Sản phẩm","Liên hệ"]}',
            },
            {
                "name": "Demo hero",
                "block_name": "demo-hero",
                "html": '<section class="demo-hero"><span>DEMO BLOCK</span><h2>Component kéo thả</h2></section>',
                "css": ".demo-hero { padding: 24px; background: #e6f1fb; border-radius: 8px; } .demo-hero span { color: #0c447c; font-size: 12px; font-weight: 700; }",
                "content": '{"title":"Component kéo thả"}',
            },
        ]

        for block in blocks:
            PageComponent.objects.update_or_create(
                block_name=block["block_name"],
                defaults={**block, "status": "published", "js": ""},
            )

        PageComponentDefinition.objects.update_or_create(
            component_key="demo-header",
            defaults={
                "name": "Demo header kéo thả",
                "prehtml": '<header class="demo-header">',
                "html": '<div class="demo-header-body"><h1>{{ title }}</h1></div>',
                "css": ".demo-header { padding: 20px; border: 1px solid #dfe3e8; } .demo-header-body h1 { margin: 0; font-size: 22px; }",
                "js": "",
                "content": '{"title":"Header demo"}',
                "backhtml": "</header>",
                "blocks": [
                    {"block_name": "demo-logo", "position": 1},
                    {"block_name": "demo-menu", "position": 2},
                    {"block_name": "demo-hero", "position": 3},
                ],
                "status": "published",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo blocks and component are ready."))
        self.stdout.write("Open #components to drag demo-logo, demo-menu and demo-hero.")
