from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

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

    @transaction.atomic
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
            content.parent = None
            content.save(update_fields=("icon", "sort_order", "is_active", "parent"))
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
            administration = MenuItem.objects.filter(menu=main_menu, label="Quản lý hành chính", parent__isnull=True).first()
            recruitment = MenuItem.objects.filter(menu=main_menu, view="recruitment").order_by("id").first()
            faq = MenuItem.objects.filter(menu=main_menu, view="faq").order_by("id").first()
            if recruitment:
                recruitment.parent = None
                recruitment.label = "Recruitment"
                recruitment.href = "#recruitment"
                recruitment.icon = "bi-person-badge"
                recruitment.required_permission = "recruitment.read"
                recruitment.sort_order = 7
                recruitment.save(update_fields=("parent", "label", "href", "icon", "required_permission", "sort_order"))
            if faq:
                faq.parent = None
                faq.label = "FAQ"
                faq.href = "#faq"
                faq.icon = "bi-question-circle"
                faq.required_permission = "faq.read"
                faq.sort_order = 8
                faq.save(update_fields=("parent", "label", "href", "icon", "required_permission", "sort_order"))
            if settings and not MenuItem.objects.filter(parent=settings, view="mail-settings").exists():
                MenuItem.objects.create(menu=main_menu, label="Mail settings", view="mail-settings", href="#mail-settings", icon="bi-envelope-paper", required_permission="auth.menu.read", parent=settings, sort_order=1)
            # Keep operational sections at the top level; older seed runs placed
            # duplicate Entities and Media entries under Settings.
            if settings:
                MenuItem.objects.filter(parent=settings, view__in=("entities", "media")).delete()
            MenuItem.objects.filter(menu=main_menu, view="content").delete()
            MenuItem.objects.filter(menu=main_menu, view="recruitment-departments").delete()
            for label, order in (("Overview", 0), ("Account", 1), ("Access management", 2), ("Monitoring", 3), ("Settings", 4), ("Entities", 5), ("Nội dung", 6), ("Recruitment", 7), ("FAQ", 8), ("Products", 9), ("Build Page", 10), ("Quản lý hành chính", 11)):
                MenuItem.objects.filter(menu=main_menu, parent__isnull=True, label=label).update(sort_order=order)
            MenuItem.objects.filter(menu=main_menu, parent__isnull=True, label="Products").update(sort_order=9)
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
                "products": ("Products", "#products", "bi-box-seam", "product.read", 9),
                "recruitment": ("Recruitment", "#recruitment", "bi-person-badge", "recruitment.read", 7),
                "faq": ("FAQ", "#faq", "bi-question-circle", "faq.read", 8),
                "dealers": ("Dealers", "#dealers", "bi-geo-alt", "dealer.read", 9),
            }
            for view, (label, href, icon, permission, order) in content_items.items():
                item = MenuItem.objects.filter(menu=main_menu, view=view).order_by("id").first()
                parent = None if view in ("products", "recruitment", "faq") else administration if view == "dealers" else content
                if view == "dealers":
                    order = 2
                if not item:
                    item = MenuItem.objects.create(
                        menu=main_menu,
                        view=view,
                        label=label,
                        href=href,
                        icon=icon,
                        required_permission=permission,
                        parent=parent,
                    )
                item.parent = parent
                item.sort_order = order
                item.label = label
                item.href = href
                item.icon = icon
                item.required_permission = permission
                item.is_active = True
                item.save(update_fields=("parent", "sort_order", "label", "href", "icon", "required_permission", "is_active"))
            MenuItem.objects.filter(menu=main_menu, parent__isnull=True, label="Products").update(sort_order=9)
            product_root = MenuItem.objects.filter(menu=main_menu, view="products").first()
            if product_root:
                MenuItem.objects.update_or_create(
                    menu=main_menu,
                    view="product-sets",
                    defaults={"label": "Catalog structure", "href": "#product-sets", "icon": "bi-collection", "required_permission": "product.read", "parent": product_root, "sort_order": 0, "is_active": True},
                )
                MenuItem.objects.update_or_create(
                    menu=main_menu,
                    view="attribute-sets",
                    defaults={"label": "Attribute sets", "href": "#attribute-sets", "icon": "bi-ui-checks-grid", "required_permission": "product.read", "parent": product_root, "sort_order": 1, "is_active": True},
                )
                MenuItem.objects.update_or_create(
                    menu=main_menu,
                    view="product-tags",
                    defaults={"label": "Product tags", "href": "#product-tags", "icon": "bi-tags", "required_permission": "product.tag.read", "parent": product_root, "sort_order": 2, "is_active": True},
                )
            for view, label, href, icon, permission, order in (
                ("pages", "Pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", 0),
                ("blocks", "Blocks", "#blocks", "bi-boxes", "page.component.read", 1),
                ("components", "Components", "#components", "bi-layers", "page.component.read", 2),
                ("forms", "Forms", "#forms", "bi-ui-checks", "page.form.read", 3),
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
        for order, (label, icon) in enumerate((("Account", "bi-person-gear"), ("Access management", "bi-shield-lock"), ("Monitoring", "bi-activity"), ("Settings", "bi-gear"), ("Nội dung", "bi-collection"), ("Products", "bi-box-seam"), ("Build Page", "bi-window-stack")), start=1):
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
            ("Products", "products", "#products", "bi-box-seam", "product.read", "Products", 0),
            ("Catalog structure", "product-sets", "#product-sets", "bi-collection", "product.read", "Products", 1),
            ("Pages", "pages", "#pages", "bi-layout-text-sidebar-reverse", "page.read", "Build Page", 0),
            ("Blocks", "blocks", "#blocks", "bi-boxes", "page.component.read", "Build Page", 1),
            ("Components", "components", "#components", "bi-layers", "page.component.read", "Build Page", 2),
            ("Forms", "forms", "#forms", "bi-ui-checks", "page.form.read", "Build Page", 3),
        )
        for label, view, href, icon, permission, parent, order in entries:
            MenuItem.objects.create(menu=main_menu, label=label, view=view, href=href, icon=icon, required_permission=permission, parent=roots.get(parent), sort_order=order)
