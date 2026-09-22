from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from ...models import Page, PageComponent, PageComponentDefinition, PageTemplate, PageVersion


class PageDraftValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("tester", "tester@example.com", "password")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.template = PageTemplate.objects.create(
            name="Home",
            key="test-home",
            regions=[
                {"id": "header", "locked": True, "maxBlocks": 1, "allowedBlocks": ["site-header"]},
                {"id": "hero", "locked": False, "maxBlocks": 1, "allowedBlocks": ["hero-slider"]},
                {"id": "main", "locked": False, "maxBlocks": None, "allowedBlocks": ["product-cards"]},
                {"id": "footer", "locked": True, "maxBlocks": 1, "allowedBlocks": ["site-footer"]},
            ],
        )
        self.page = Page.objects.create(name="Home page", slug="test-home", template=self.template, template_key=self.template.key)
        self.version = PageVersion.objects.create(page=self.page, regions={"hero": []}, version_number=1, created_by=self.user)
        self.page.draft_version = self.version
        self.page.save(update_fields=["draft_version"])

    def test_patch_rejects_block_not_allowed_in_region(self):
        response = self.client.patch("/api/pages/test-home/draft/", {"regions": {"hero": [{"type": "exchange-rate-table", "props": {}}]}}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("exchange-rate-table", response.data["detail"])
        self.assertIn("hero", response.data["detail"])
        self.version.refresh_from_db()
        self.assertEqual(self.version.regions, {"hero": []})

    def test_create_page_links_template_and_can_load_draft(self):
        response = self.client.post(
            "/api/pages/",
            {"name": "Landing page", "slug": "landing-page", "template_key": self.template.key, "status": "draft", "components": []},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created = Page.objects.get(slug="landing-page")
        self.assertEqual(created.template_id, self.template.id)
        draft = self.client.patch(
            "/api/pages/landing-page/draft/",
            {"regions": {"hero": []}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200)

    def test_create_page_rejects_unknown_template(self):
        response = self.client.post(
            "/api/pages/",
            {"name": "Broken page", "slug": "broken-page", "template_key": "missing-template", "status": "draft", "components": []},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing-template", response.data["detail"])

    def test_patch_accepts_allowed_block_and_publish_creates_version(self):
        draft = {"hero": [{"type": "hero-slider", "props": {"slides": []}}]}
        response = self.client.patch("/api/pages/test-home/draft/", {"regions": draft}, format="json")
        self.assertEqual(response.status_code, 200)
        published = self.client.post("/api/pages/test-home/publish/")
        self.assertEqual(published.status_code, 200)
        self.page.refresh_from_db()
        self.assertIsNotNone(self.page.published_version_id)
        self.assertEqual(self.page.published_version.regions, draft)
        self.assertEqual(self.page.published_version.version_number, 2)

    def test_preview_content_returns_empty_items_for_unavailable_source(self):
        response = self.client.post(
            "/api/pages/test-home/preview-content/",
            {"block": {"type": "news-list", "props": {"source": {"api": "not-a-url"}}}},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["block"]["props"]["items"], [])

    def test_patch_accepts_registered_component_in_unlocked_region(self):
        PageComponentDefinition.objects.create(name="Demo header", component_key="demo-header")
        response = self.client.patch(
            "/api/pages/test-home/draft/",
            {"regions": {"hero": [{"type": "demo-header", "props": {}}]}},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["version"]["regions"]["hero"][0]["type"], "demo-header")

    def test_patch_rejects_reusable_block_in_page_region(self):
        PageComponent.objects.create(name="Reusable logo", block_name="demo-logo")
        response = self.client.patch(
            "/api/pages/test-home/draft/",
            {"regions": {"hero": [{"type": "demo-logo", "props": {}}]}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_component_crud_persists_html_css_js_and_content(self):
        payload = {
            "name": "Promo banner",
            "block_name": "promo-banner",
            "html": "<section>{{ title }}</section>",
            "css": ".promo { color: red; }",
            "js": "console.log('promo');",
            "content": "{\"title\":\"Hello\"}",
            "status": "draft",
        }
        created = self.client.post("/api/pages/components/", payload, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["block_name"], "promo-banner")
        self.assertEqual(PageComponent.objects.get(pk=created.data["id"]).content, payload["content"])

        duplicate = self.client.post("/api/pages/components/", payload, format="json")
        self.assertEqual(duplicate.status_code, 400)
        updated = self.client.patch(f"/api/pages/components/{created.data['id']}/", {**payload, "name": "Updated banner"}, format="json")
        self.assertEqual(updated.status_code, 200)
        deleted = self.client.delete(f"/api/pages/components/{created.data['id']}/")
        self.assertEqual(deleted.status_code, 204)

    def test_component_definition_crud_persists_editors_and_ordered_blocks(self):
        PageComponent.objects.create(name="Logo block", block_name="logo-block")
        PageComponent.objects.create(name="Menu block", block_name="menu-block")
        payload = {
            "name": "Header component",
            "component_key": "header-component",
            "prehtml": "<header>",
            "html": "<nav>{{ title }}</nav>",
            "css": ".header { display: flex; }",
            "js": "console.log('header');",
            "content": '{"title":"Hello"}',
            "backhtml": "</header>",
            "blocks": ["logo-block", "menu-block"],
            "status": "draft",
        }
        created = self.client.post("/api/pages/component-definitions/", payload, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["blocks"], [{"block_name": "logo-block", "position": 1}, {"block_name": "menu-block", "position": 2}])
        self.assertEqual(created.data["prehtml"], payload["prehtml"])
        self.assertEqual(created.data["backhtml"], payload["backhtml"])

        updated = self.client.patch(
            f"/api/pages/component-definitions/{created.data['id']}/",
            {**payload, "blocks": ["menu-block", "logo-block"]},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["blocks"], [{"block_name": "menu-block", "position": 1}, {"block_name": "logo-block", "position": 2}])

    def test_component_definition_rejects_missing_reusable_block(self):
        response = self.client.post(
            "/api/pages/component-definitions/",
            {"name": "Broken component", "component_key": "broken-component", "blocks": ["missing-block"]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing-block", response.data["detail"])
