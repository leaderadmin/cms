from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api.models import Menu, MenuItem, Role, RoutePermission


class Command(BaseCommand):
    help = "Create repeatable demo users and dynamic RBAC roles."

    def handle(self, *args, **options):
        User = get_user_model()
        permissions = {
            item.code: item
            for item in RoutePermission.objects.all()
        }
        all_permissions = list(permissions.values())
        role_permissions = {
            "user": [
                permissions["auth.me.read"],
                permissions["dashboard.stats.read"],
                permissions["auth.sessions.read"],
                permissions["auth.menu.read"],
            ],
            "support": [
                permissions["auth.me.read"],
                permissions["auth.sessions.read"],
                permissions["auth.menu.read"],
            ],
            "admin": all_permissions,
        }
        for role_name, declared_permissions in role_permissions.items():
            role, _ = Role.objects.get_or_create(name=role_name)
            role.permissions.set(declared_permissions)

        self.seed_menu()

        demo_users = (
            ("demo-admin", "DemoAdmin123!", "admin"),
            ("demo-user", "DemoUser123!", "user"),
            ("demo-support", "Abc@123", "support"),
        )
        for username, password, role_name in demo_users:
            user, _ = User.objects.get_or_create(username=username)
            user.email = f"{username}@example.test"
            user.set_password(password)
            user.save(update_fields=("email", "password"))
            user.dynamic_roles.set([Role.objects.get(name=role_name)])

        self.stdout.write(self.style.SUCCESS("Auth demo users and roles are ready."))
        self.stdout.write("demo-admin / DemoAdmin123!")
        self.stdout.write("demo-user / DemoUser123!")
        self.stdout.write("demo-support / Abc@123")

    def seed_menu(self):
        main_menu, _ = Menu.objects.get_or_create(name="Main menu", slug="main")
        MenuItem.objects.filter(menu__isnull=True).update(menu=main_menu)
        if MenuItem.objects.exists():
            settings = MenuItem.objects.filter(label="Settings", parent__isnull=True).first()
            content, _ = MenuItem.objects.get_or_create(
                menu=main_menu,
                label="Nội dung",
                parent=None,
                defaults={"icon": "bi-collection", "sort_order": 5},
            )
            content.icon = "bi-collection"
            content.sort_order = 5
            content.is_active = True
            content.save(update_fields=("icon", "sort_order", "is_active"))
            build_page, _ = MenuItem.objects.get_or_create(
                menu=main_menu,
                label="Build Page",
                parent=None,
                defaults={"icon": "bi-window-stack", "sort_order": 6},
            )
            build_page.icon = "bi-window-stack"
            build_page.sort_order = 6
            build_page.is_active = True
            build_page.save(update_fields=("icon", "sort_order", "is_active"))
            if settings and not MenuItem.objects.filter(parent=settings, view="mail-settings").exists():
                MenuItem.objects.create(menu=main_menu, label="Mail settings", view="mail-settings", href="#mail-settings", icon="bi-envelope-paper", required_permission="auth.menu.read", parent=settings, sort_order=1)
            if settings and not MenuItem.objects.filter(parent=settings, view="entities").exists():
                MenuItem.objects.create(menu=main_menu, label="Entities", view="entities", href="#entities", icon="bi-boxes", required_permission="entity.read", parent=settings, sort_order=3)
            if settings and not MenuItem.objects.filter(parent=settings, view="media").exists():
                MenuItem.objects.create(menu=main_menu, label="Media", view="media", href="#media", icon="bi-images", required_permission="media.read", parent=settings, sort_order=4)
            if not MenuItem.objects.filter(view="articles").exists():
                MenuItem.objects.create(menu=main_menu, label="Articles", view="articles", href="#articles", icon="bi-file-earmark-richtext", required_permission="article.read", sort_order=5)
            if not MenuItem.objects.filter(view="categories").exists():
                MenuItem.objects.create(menu=main_menu, label="Categories", view="categories", href="#categories", icon="bi-tags", required_permission="article.category.read", sort_order=6)
            if not MenuItem.objects.filter(view="tags").exists():
                MenuItem.objects.create(menu=main_menu, label="Tags", view="tags", href="#tags", icon="bi-hash", required_permission="article.tag.read", sort_order=7)
            if not MenuItem.objects.filter(view="pages").exists():
                MenuItem.objects.create(menu=main_menu, label="Pages", view="pages", href="#pages", icon="bi-layout-text-sidebar-reverse", required_permission="page.read", sort_order=8)
            content_items = {
                "articles": ("Articles", "#articles", "bi-file-earmark-richtext", "article.read", 0),
                "categories": ("Categories", "#categories", "bi-tags", "article.category.read", 1),
                "tags": ("Tags", "#tags", "bi-hash", "article.tag.read", 2),
                "pages": ("Pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", 3),
                "media": ("Media", "#media", "bi-images", "media.read", 4),
            }
            for view, (label, href, icon, permission, order) in content_items.items():
                item = MenuItem.objects.filter(menu=main_menu, view=view).first()
                if item:
                    item.parent = content
                    item.sort_order = order
                    item.label = label
                    item.href = href
                    item.icon = icon
                    item.required_permission = permission
                    item.save(update_fields=("parent", "sort_order", "label", "href", "icon", "required_permission"))
            for view, label, href, icon, permission, order in (
                ("pages", "Pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", 0),
                ("blocks", "Blocks", "#blocks", "bi-boxes", "page.component.read", 1),
                ("components", "Components", "#components", "bi-layers", "page.component.read", 2),
            ):
                item = MenuItem.objects.filter(menu=main_menu, view=view).first()
                if view == "blocks" and not item:
                    item = MenuItem.objects.filter(menu=main_menu, view="components").first()
                if not item:
                    MenuItem.objects.create(menu=main_menu, label=label, view=view, href=href, icon=icon, required_permission=permission, parent=build_page, sort_order=order)
                else:
                    item.view = view
                    item.parent = build_page
                    item.label = label
                    item.href = href
                    item.icon = icon
                    item.required_permission = permission
                    item.sort_order = order
                    item.save(update_fields=("view", "parent", "label", "href", "icon", "required_permission", "sort_order"))
            return
        roots = {}
        MenuItem.objects.create(menu=main_menu, label="Overview", href="#overview", view="overview", icon="bi-speedometer2", required_permission="dashboard.stats.read", sort_order=0)
        for order, (label, icon) in enumerate((("Account", "bi-person-gear"), ("Access management", "bi-shield-lock"), ("Monitoring", "bi-activity"), ("Settings", "bi-gear"), ("Nội dung", "bi-collection"), ("Build Page", "bi-window-stack")), start=1):
            roots[label] = MenuItem.objects.create(menu=main_menu, label=label, icon=icon, sort_order=order)
        entries = (
            ("General settings", "settings", "#settings", "bi-sliders", "auth.menu.read", "Settings", 0),
            ("Mail settings", "mail-settings", "#mail-settings", "bi-envelope-paper", "auth.menu.read", "Settings", 1),
            ("Profile", "profile", "#profile", "bi-person-circle", "auth.me.read", "Account", 0),
            ("Users", "users", "#users", "bi-people", "auth.users.read", "Access management", 0),
            ("Roles & Permissions", "roles", "#roles", "bi-shield-check", "auth.roles.read", "Access management", 1),
            ("Activity logs", "activity", "#activity-logs", "bi-journal-text", "audit.logs.read", "Monitoring", 0),
            ("Sessions", "sessions", "#sessions", "bi-shield-lock", "auth.sessions.read", "Monitoring", 1),
            ("Menu builder", "menu-builder", "#menu-builder", "bi-diagram-3", "auth.menu.create", "Settings", 2),
            ("Entities", "entities", "#entities", "bi-boxes", "entity.read", "Settings", 3),
            ("Articles", "articles", "#articles", "bi-file-earmark-richtext", "article.read", "Nội dung", 0),
            ("Categories", "categories", "#categories", "bi-tags", "article.category.read", "Nội dung", 1),
            ("Tags", "tags", "#tags", "bi-hash", "article.tag.read", "Nội dung", 2),
            ("Pages", "pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", "Nội dung", 3),
            ("Media", "media", "#media", "bi-images", "media.read", "Nội dung", 4),
            ("Pages", "pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", "Build Page", 0),
            ("Blocks", "blocks", "#blocks", "bi-boxes", "page.component.read", "Build Page", 1),
            ("Components", "components", "#components", "bi-layers", "page.component.read", "Build Page", 2),
        )
        for label, view, href, icon, permission, parent, order in entries:
            MenuItem.objects.create(menu=main_menu, label=label, view=view, href=href, icon=icon, required_permission=permission, parent=roots.get(parent), sort_order=order)
