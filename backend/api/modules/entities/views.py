from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from .permissions import ENTITY_CREATE, ENTITY_DELETE, ENTITY_READ, ENTITY_UPDATE
from .registry import ENTITY_MODELS, field_metadata, get_entity
from .serializers import save_record, serialize_record
from .schema import add_column, alter_column, drop_column, rename_column, schema_catalog, table_schema


class SchemaCatalogView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = ENTITY_READ

    def get(self, request):
        return Response(schema_catalog())


class SchemaTableView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": ENTITY_READ, "POST": ENTITY_CREATE}

    def get(self, request, table_name):
        schema = table_schema(table_name)
        if schema is None:
            return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(schema)

    def post(self, request, table_name):
        try:
            add_column(table_name, request.data)
        except Exception as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(table_schema(table_name), status=status.HTTP_201_CREATED)


class SchemaColumnView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": ENTITY_UPDATE, "DELETE": ENTITY_DELETE}

    def patch(self, request, table_name, column_name):
        try:
            if "name" in request.data and len(request.data) == 1:
                rename_column(table_name, column_name, request.data.get("name", ""))
            else:
                alter_column(table_name, column_name, request.data)
        except Exception as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(table_schema(table_name))

    def delete(self, request, table_name, column_name):
        try:
            drop_column(table_name, column_name)
        except Exception as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(table_schema(table_name))


class EntityCatalogView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = ENTITY_READ

    def get(self, request):
        return Response([{"slug": slug, "label": label, "fields": field_metadata(model, slug)} for slug, (label, model) in ENTITY_MODELS.items()])


class EntityListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": ENTITY_READ, "POST": ENTITY_CREATE}

    def get(self, request, slug):
        entity = get_entity(slug)
        if entity is None:
            return Response({"detail": "Entity table not found."}, status=status.HTTP_404_NOT_FOUND)
        _, model = entity
        search = request.query_params.get("q", "").strip()
        queryset = model.objects.all()
        if search:
            query = Q()
            for field in model._meta.fields:
                if field.get_internal_type() in ("CharField", "TextField", "SlugField", "EmailField"):
                    query |= Q(**{f"{field.name}__icontains": search})
            if query:
                queryset = queryset.filter(query)
        return Response([serialize_record(item) for item in queryset[:200]])

    def post(self, request, slug):
        entity = get_entity(slug)
        if entity is None:
            return Response({"detail": "Entity table not found."}, status=status.HTTP_404_NOT_FOUND)
        _, model = entity
        try:
            item = save_record(model, slug, request.data)
        except ValidationError as error:
            return Response({"detail": error.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_record(item), status=status.HTTP_201_CREATED)


class EntityDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": ENTITY_UPDATE, "DELETE": ENTITY_DELETE}

    def get_object(self, slug, pk):
        entity = get_entity(slug)
        if entity is None:
            return None, None
        _, model = entity
        try:
            return model.objects.get(pk=pk), model
        except model.DoesNotExist:
            return None, model

    def patch(self, request, slug, pk):
        item, model = self.get_object(slug, pk)
        if item is None:
            return Response({"detail": "Entity record not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            item = save_record(model, slug, request.data, item)
        except ValidationError as error:
            return Response({"detail": error.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_record(item))

    def delete(self, request, slug, pk):
        item, _ = self.get_object(slug, pk)
        if item is None:
            return Response({"detail": "Entity record not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)