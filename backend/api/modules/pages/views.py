from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from ...models import DynamicForm, Page, PageComponent, PageComponentDefinition, PageTemplate, PageVersion
from .permissions import COMPONENT_CREATE, COMPONENT_DELETE, COMPONENT_READ, COMPONENT_UPDATE, FORM_CREATE, FORM_DELETE, FORM_READ, FORM_UPDATE, PAGE_CREATE, PAGE_DELETE, PAGE_READ, PAGE_UPDATE
from .serializers import component_definition_payload, component_payload, form_payload, page_payload, serialize_component, serialize_component_definition, serialize_form, serialize_page, serialize_template, serialize_version, template_payload
from .validation import validate_regions_against_template
from .content_resolver import resolve_content


def page_by_slug(slug):
    return Page.objects.select_related("template", "published_version", "draft_version").filter(slug=slug).first()


def resolve_published_regions(regions):
    resolved = {}
    for region_key, blocks in (regions or {}).items():
        resolved[region_key] = [resolve_content(block) for block in blocks] if isinstance(blocks, list) else []
    return resolved


def published_component_definitions(regions):
    keys = {
        block.get("type")
        for blocks in (regions or {}).values()
        if isinstance(blocks, list)
        for block in blocks
        if isinstance(block, dict) and block.get("type")
    }
    definitions = PageComponentDefinition.objects.filter(component_key__in=keys, status=Page.STATUS_PUBLISHED)
    return [serialize_component_definition(definition) for definition in definitions]


class DynamicFormListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": FORM_READ, "POST": FORM_CREATE}

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        forms = DynamicForm.objects.all()
        if query:
            forms = forms.filter(Q(name__icontains=query) | Q(short_code__icontains=query))
        return Response([serialize_form(form) for form in forms])

    def post(self, request):
        payload, error = form_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            form = DynamicForm.objects.create(**payload)
        except IntegrityError:
            return Response({"detail": "A form with this short code already exists."}, status=400)
        return Response(serialize_form(form), status=201)


class DynamicFormDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": FORM_UPDATE, "DELETE": FORM_DELETE}

    def patch(self, request, form_id):
        form = DynamicForm.objects.filter(pk=form_id).first()
        if not form:
            return Response({"detail": "Form not found."}, status=404)
        payload, error = form_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            for field, value in payload.items():
                setattr(form, field, value)
            form.save()
        except IntegrityError:
            return Response({"detail": "A form with this short code already exists."}, status=400)
        return Response(serialize_form(form))

    def delete(self, request, form_id):
        deleted, _ = DynamicForm.objects.filter(pk=form_id).delete()
        if not deleted:
            return Response({"detail": "Form not found."}, status=404)
        return Response(status=204)


class PublishedPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        page = page_by_slug(slug)
        if not page or not page.published_version:
            return Response({"detail": "Published page not found."}, status=404)
        regions = resolve_published_regions(page.published_version.regions)
        return Response({"page": serialize_page(page), "template": serialize_template(page.template), "components": published_component_definitions(regions), "version": serialize_version(page.published_version, regions=regions)})


class DraftPageView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PAGE_READ, "PATCH": PAGE_UPDATE}

    def get(self, request, slug):
        page = page_by_slug(slug)
        if not page or not page.draft_version:
            return Response({"detail": "Draft page not found."}, status=404)
        return Response({"page": serialize_page(page), "version": serialize_version(page.draft_version)})

    def patch(self, request, slug):
        page = page_by_slug(slug)
        if not page or not page.template:
            return Response({"detail": "Draft page or template not found."}, status=404)
        regions = request.data.get("regions")
        error = validate_regions_against_template(regions, page.template)
        if error:
            return Response({"detail": error}, status=400)
        with transaction.atomic():
            version = page.draft_version
            if version is None:
                version = PageVersion.objects.create(page=page, regions=regions, version_number=1, created_by=request.user)
                page.draft_version = version
                page.save(update_fields=["draft_version", "updated_at"])
            else:
                version.regions = regions
                version.created_by = request.user
                version.save(update_fields=["regions", "created_by"])
        return Response({"page": serialize_page(page), "version": serialize_version(version)})


class PublishPageView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"POST": PAGE_UPDATE}

    def post(self, request, slug):
        page = page_by_slug(slug)
        if not page or not page.template or not page.draft_version:
            return Response({"detail": "Draft page or template not found."}, status=404)
        error = validate_regions_against_template(page.draft_version.regions, page.template)
        if error:
            return Response({"detail": error}, status=400)
        with transaction.atomic():
            next_number = (page.versions.order_by("-version_number").values_list("version_number", flat=True).first() or 0) + 1
            version = PageVersion.objects.create(page=page, regions=page.draft_version.regions, version_number=next_number, created_by=request.user)
            page.published_version = version
            page.status = Page.STATUS_PUBLISHED
            page.save(update_fields=["published_version", "status", "updated_at"])
        return Response({"page": serialize_page(page), "version": serialize_version(version)})


class PreviewContentView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"POST": PAGE_READ}

    def post(self, request, slug):
        page = page_by_slug(slug)
        if not page:
            return Response({"detail": "Page not found."}, status=404)
        block = request.data.get("block")
        if not isinstance(block, dict) or not isinstance(block.get("props"), dict):
            return Response({"detail": "A block with props is required."}, status=400)
        return Response({"block": resolve_content(block, limit=5)})


class PageTemplateListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PAGE_READ, "POST": PAGE_CREATE}

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        templates = PageTemplate.objects.all()
        if query:
            templates = templates.filter(Q(name__icontains=query) | Q(key__icontains=query))
        return Response([serialize_template(template) for template in templates])

    def post(self, request):
        payload, error = template_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            template = PageTemplate.objects.create(**payload)
        except IntegrityError:
            return Response({"detail": "A template with this key already exists."}, status=400)
        return Response(serialize_template(template), status=201)


class PageTemplateDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PAGE_READ, "PATCH": PAGE_UPDATE, "DELETE": PAGE_DELETE}

    def get(self, request, template_id):
        template = PageTemplate.objects.filter(pk=template_id).first()
        if not template:
            return Response({"detail": "Template not found."}, status=404)
        return Response(serialize_template(template))

    def patch(self, request, template_id):
        template = PageTemplate.objects.filter(pk=template_id).first()
        if not template:
            return Response({"detail": "Template not found."}, status=404)
        payload, error = template_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            for field, value in payload.items():
                setattr(template, field, value)
            template.save()
        except IntegrityError:
            return Response({"detail": "A template with this key already exists."}, status=400)
        return Response(serialize_template(template))


class PageComponentListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": COMPONENT_READ, "POST": COMPONENT_CREATE}

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        components = PageComponent.objects.all()
        if query:
            components = components.filter(Q(name__icontains=query) | Q(block_name__icontains=query))
        return Response([serialize_component(component) for component in components])

    def post(self, request):
        payload, error = component_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                component = PageComponent.objects.create(**payload)
        except IntegrityError:
            return Response({"detail": "A component with this block name already exists."}, status=400)
        return Response(serialize_component(component), status=201)


class PageComponentDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": COMPONENT_UPDATE, "DELETE": COMPONENT_DELETE}

    def patch(self, request, component_id):
        component = PageComponent.objects.filter(pk=component_id).first()
        if not component:
            return Response({"detail": "Component not found."}, status=404)
        payload, error = component_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                for field, value in payload.items():
                    setattr(component, field, value)
                component.save()
        except IntegrityError:
            return Response({"detail": "A component with this block name already exists."}, status=400)
        return Response(serialize_component(component))

    def delete(self, request, component_id):
        deleted, _ = PageComponent.objects.filter(pk=component_id).delete()
        if not deleted:
            return Response({"detail": "Component not found."}, status=404)
        return Response(status=204)


class PageComponentDefinitionListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": COMPONENT_READ, "POST": COMPONENT_CREATE}

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        components = PageComponentDefinition.objects.all()
        if query:
            components = components.filter(Q(name__icontains=query) | Q(component_key__icontains=query))
        return Response([serialize_component_definition(component) for component in components])

    def post(self, request):
        payload, error = component_definition_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            component = PageComponentDefinition.objects.create(**payload)
        except IntegrityError:
            return Response({"detail": "A component with this key already exists."}, status=400)
        return Response(serialize_component_definition(component), status=201)


class PageComponentDefinitionDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": COMPONENT_UPDATE, "DELETE": COMPONENT_DELETE}

    def patch(self, request, component_id):
        component = PageComponentDefinition.objects.filter(pk=component_id).first()
        if not component:
            return Response({"detail": "Component not found."}, status=404)
        payload, error = component_definition_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            for field, value in payload.items():
                setattr(component, field, value)
            component.save()
        except IntegrityError:
            return Response({"detail": "A component with this key already exists."}, status=400)
        return Response(serialize_component_definition(component))

    def delete(self, request, component_id):
        deleted, _ = PageComponentDefinition.objects.filter(pk=component_id).delete()
        if not deleted:
            return Response({"detail": "Component not found."}, status=404)
        return Response(status=204)

class PageListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PAGE_READ, "POST": PAGE_CREATE}

    def get(self, request):
        pages = Page.objects.select_related("created_by").all()
        query = request.query_params.get("q", "").strip()
        status = request.query_params.get("status", "").strip()
        if query:
            pages = pages.filter(Q(name__icontains=query) | Q(slug__icontains=query))
        if status:
            pages = pages.filter(status=status)
        return Response([serialize_page(page) for page in pages])

    def post(self, request):
        payload, error = page_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        template = PageTemplate.objects.filter(key=payload["template_key"]).first()
        if not template:
            return Response({"detail": f"Template '{payload['template_key']}' not found."}, status=400)
        try:
            page = Page.objects.create(created_by=request.user, template=template, **payload)
        except IntegrityError:
            return Response({"detail": "A page with this slug already exists."}, status=400)
        return Response(serialize_page(page), status=201)


class PageDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PAGE_READ, "PATCH": PAGE_UPDATE, "DELETE": PAGE_DELETE}

    def get(self, request, page_id):
        page = Page.objects.select_related("created_by").filter(pk=page_id).first()
        if not page:
            return Response({"detail": "Page not found."}, status=404)
        return Response(serialize_page(page))

    def patch(self, request, page_id):
        page = Page.objects.filter(pk=page_id).first()
        if not page:
            return Response({"detail": "Page not found."}, status=404)
        payload, error = page_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        template = PageTemplate.objects.filter(key=payload["template_key"]).first()
        if not template:
            return Response({"detail": f"Template '{payload['template_key']}' not found."}, status=400)
        try:
            for field, value in payload.items():
                setattr(page, field, value)
            page.template = template
            page.save()
        except IntegrityError:
            return Response({"detail": "A page with this slug already exists."}, status=400)
        return Response(serialize_page(page))

    def delete(self, request, page_id):
        updated = Page.objects.filter(pk=page_id).update(status=Page.STATUS_ARCHIVED)
        if not updated:
            return Response({"detail": "Page not found."}, status=404)
        return Response(status=204)
