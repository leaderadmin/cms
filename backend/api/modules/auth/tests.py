from django.test import TestCase

from ...models import Menu, MenuItem, RoutePermission
from .serializers import MenuItemSerializer


class MenuItemValidationTests(TestCase):
    def setUp(self):
        self.menu = Menu.objects.create(name="Main", slug="test-main")
        self.permission, _ = RoutePermission.objects.get_or_create(
            code="article.read",
            defaults={"module": "articles", "route": "GET /api/articles/"},
        )

    def test_rejects_unknown_required_permission(self):
        serializer = MenuItemSerializer(data={
            "menu_id": self.menu.id,
            "label": "Articles",
            "href": "#articles",
            "view": "articles",
            "icon": "bi-file",
            "required_permission": "article.missing",
            "parent_id": None,
            "sort_order": 0,
            "is_active": True,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("required_permission", serializer.errors)

    def test_accepts_existing_required_permission(self):
        serializer = MenuItemSerializer(data={
            "menu_id": self.menu.id,
            "label": "Articles",
            "href": "#articles",
            "view": "articles",
            "icon": "bi-file",
            "required_permission": self.permission.code,
            "parent_id": None,
            "sort_order": 0,
            "is_active": True,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_parent_from_another_menu(self):
        other_menu = Menu.objects.create(name="Other", slug="other-menu")
        parent = MenuItem.objects.create(menu=other_menu, label="Other root")
        serializer = MenuItemSerializer(data={
            "menu_id": self.menu.id,
            "label": "Child",
            "required_permission": self.permission.code,
            "parent_id": parent.id,
            "is_active": True,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("parent_id", serializer.errors)
