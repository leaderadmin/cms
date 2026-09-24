from django.db import transaction
from django.db.models import Q
from collections import defaultdict
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from ...models import MediaFile, Product, ProductAttribute, ProductAttributeSet, ProductCategory, ProductGroup, ProductTag, ProductTranslation, ProductType
from .permissions import PRODUCT_CREATE, PRODUCT_DELETE, PRODUCT_METADATA_CREATE, PRODUCT_METADATA_READ, PRODUCT_PUBLISH, PRODUCT_READ, PRODUCT_TAG_CREATE, PRODUCT_TAG_DELETE, PRODUCT_TAG_READ, PRODUCT_TAG_UPDATE, PRODUCT_UPDATE
from .serializers import metadata_payload, product_payload, serialize_attribute, serialize_attribute_set, serialize_category, serialize_group, serialize_product, serialize_product_tag, serialize_type, tag_payload


class ProductMetadataView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PRODUCT_METADATA_READ, "POST": PRODUCT_METADATA_CREATE, "PATCH": PRODUCT_METADATA_CREATE}

    def get(self, request):
        products_by_group = defaultdict(list)
        for product in Product.objects.filter(status__gte=Product.STATUS_DRAFT).prefetch_related("translations"):
            products_by_group[product.kind].append(product)
        return Response({
            "groups": [serialize_group(item, products_by_group) for item in ProductGroup.objects.filter(status=1)],
            "types": [serialize_type(item, products_by_group) for item in ProductType.objects.filter(status=1).prefetch_related("groups")],
            "categories": [serialize_category(item) for item in ProductCategory.objects.filter(status=1).select_related("product_type")],
            "attributes": [serialize_attribute(item) for item in ProductAttribute.objects.filter(status=1)],
            "attribute_sets": [serialize_attribute_set(item) for item in ProductAttributeSet.objects.filter(status=1).prefetch_related("attributes")],
            "product_tags": [serialize_product_tag(item) for item in ProductTag.objects.all()],
        })

    def post(self, request):
        kind = str(request.data.get("kind") or "type")
        models = {"group": ProductGroup, "type": ProductType, "category": ProductCategory, "attribute": ProductAttribute, "attribute_set": ProductAttributeSet}
        model = models.get(kind)
        if not model:
            return Response({"detail": "Invalid metadata kind."}, status=400)
        payload, error = metadata_payload(request.data, model)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                if model is ProductCategory:
                    item = model.objects.create(**{key: value for key, value in payload.items() if key not in {"parent_id", "product_type_id"}}, parent_id=payload["parent_id"], product_type_id=payload["product_type_id"])
                elif model is ProductAttributeSet:
                    attribute_ids = payload.pop("attribute_ids")
                    item = model.objects.create(**payload)
                    item.attributes.set(ProductAttribute.objects.filter(id__in=attribute_ids))
                else:
                    item = model.objects.create(**payload)
        except Exception:
            return Response({"detail": "Metadata name or slug already exists."}, status=400)
        serializer = serialize_group if model is ProductGroup else serialize_type if model is ProductType else serialize_category if model is ProductCategory else serialize_attribute if model is ProductAttribute else serialize_attribute_set
        return Response(serializer(item), status=201)

    def patch(self, request, metadata_id):
        kind = str(request.data.get("kind") or "type")
        models = {"group": ProductGroup, "type": ProductType, "category": ProductCategory, "attribute": ProductAttribute, "attribute_set": ProductAttributeSet}
        model = models.get(kind)
        if not model:
            return Response({"detail": "Invalid metadata kind."}, status=400)
        item = model.objects.filter(pk=metadata_id).first()
        if not item:
            return Response({"detail": "Metadata item not found."}, status=404)
        payload, error = metadata_payload(request.data, model)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                attribute_ids = payload.pop("attribute_ids", None)
                for key, value in payload.items():
                    setattr(item, key, value)
                item.save()
                if model is ProductAttributeSet and attribute_ids is not None:
                    item.attributes.set(ProductAttribute.objects.filter(id__in=attribute_ids))
        except Exception:
            return Response({"detail": "Metadata name or slug already exists."}, status=400)
        serializer = serialize_group if model is ProductGroup else serialize_type if model is ProductType else serialize_category if model is ProductCategory else serialize_attribute if model is ProductAttribute else serialize_attribute_set
        return Response(serializer(item))


class ProductListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PRODUCT_READ, "POST": PRODUCT_CREATE}

    def get(self, request):
        queryset = Product.objects.select_related("product_type", "category", "attribute_set", "image").prefetch_related("translations", "attribute_set__attributes")
        query = request.query_params.get("q", "").strip()
        kind = request.query_params.get("kind", "").strip()
        status = request.query_params.get("status", "").strip()
        language = request.query_params.get("language", "").strip() or None
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(slug__icontains=query) | Q(translations__title__icontains=query))
        if kind:
            queryset = queryset.filter(kind=kind)
        if status:
            queryset = queryset.filter(status=status)
        queryset = queryset.distinct()
        try:
            page = max(1, int(request.query_params.get("page", 1)))
            page_size = min(100, max(1, int(request.query_params.get("page_size", 25))))
        except (TypeError, ValueError):
            page, page_size = 1, 25
        total = queryset.count()
        start = (page - 1) * page_size
        return Response({"count": total, "page": page, "page_size": page_size, "next": page + 1 if start + page_size < total else None, "previous": page - 1 if page > 1 and start < total else None, "results": [serialize_product(item, language) for item in queryset[start:start + page_size]]})

    def post(self, request):
        payload, error = product_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        error = self._validate_references(payload)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                product = self._save_product(Product(created_by=request.user), payload)
        except Exception:
            return Response({"detail": "A product with this slug may already exist."}, status=400)
        return Response(serialize_product(product), status=201)

    @staticmethod
    def _validate_references(payload):
        if payload["product_type_id"] and not ProductType.objects.filter(pk=payload["product_type_id"], status=1).exists():
            return "Product type was not found."
        if payload["category_id"] and not ProductCategory.objects.filter(pk=payload["category_id"], status=1).exists():
            return "Product category was not found."
        if payload["attribute_set_id"] and not ProductAttributeSet.objects.filter(pk=payload["attribute_set_id"], status=1).exists():
            return "Attribute set was not found."
        if payload["image_id"] and not MediaFile.objects.filter(pk=payload["image_id"], content_type__startswith="image/").exists():
            return "Selected product image was not found."
        return None

    @staticmethod
    def _save_product(product, payload):
        for field in ("name", "slug", "kind", "status", "ordering", "is_featured", "attributes", "extra_data"):
            setattr(product, field, payload[field])
        product.product_type_id = payload["product_type_id"]
        product.category_id = payload["category_id"]
        product.attribute_set_id = payload["attribute_set_id"]
        product.image_id = payload["image_id"]
        product.save()
        product.managed_tags.set(ProductTag.objects.filter(id__in=payload["tag_ids"]))
        for item in payload["translations"]:
            ProductTranslation.objects.update_or_create(product=product, language_code=item["language_code"], defaults=item)
        return product


class ProductDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PRODUCT_READ, "PATCH": PRODUCT_UPDATE, "DELETE": PRODUCT_DELETE}

    def get(self, request, product_id):
        product = Product.objects.select_related("product_type", "category", "attribute_set", "image").prefetch_related("translations", "attribute_set__attributes").filter(pk=product_id).first()
        if not product:
            return Response({"detail": "Product not found."}, status=404)
        return Response(serialize_product(product, request.query_params.get("language")))

    def patch(self, request, product_id):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            return Response({"detail": "Product not found."}, status=404)
        payload, error = product_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        error = ProductListView._validate_references(payload)
        if error:
            return Response({"detail": error}, status=400)
        try:
            with transaction.atomic():
                product = ProductListView._save_product(product, payload)
        except Exception:
            return Response({"detail": "A product with this slug may already exist."}, status=400)
        return Response(serialize_product(product))

    def delete(self, request, product_id):
        updated = Product.objects.filter(pk=product_id).update(status=Product.STATUS_ARCHIVED)
        if not updated:
            return Response({"detail": "Product not found."}, status=404)
        return Response(status=204)


class ProductPublishView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = PRODUCT_PUBLISH

    def post(self, request, product_id):
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            return Response({"detail": "Product not found."}, status=404)
        product.status = Product.STATUS_ACTIVE
        product.translations.update(status=Product.STATUS_ACTIVE)
        product.save(update_fields=("status", "updated_at"))
        return Response(serialize_product(product, request.data.get("language")))


class ProductTagListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PRODUCT_TAG_READ, "POST": PRODUCT_TAG_CREATE}

    def get(self, request):
        tags = ProductTag.objects.all()
        query = request.query_params.get("q", "").strip()
        if query:
            tags = tags.filter(Q(name__icontains=query) | Q(slug__icontains=query))
        return Response([serialize_product_tag(tag) for tag in tags])

    def post(self, request):
        payload, error = tag_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            tag = ProductTag.objects.create(**payload)
        except Exception:
            return Response({"detail": "A product tag with this name or slug already exists."}, status=400)
        return Response(serialize_product_tag(tag), status=201)


class ProductTagDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": PRODUCT_TAG_READ, "PATCH": PRODUCT_TAG_UPDATE, "DELETE": PRODUCT_TAG_DELETE}

    def patch(self, request, tag_id):
        tag = ProductTag.objects.filter(pk=tag_id).first()
        if not tag:
            return Response({"detail": "Product tag not found."}, status=404)
        payload, error = tag_payload(request.data, tag)
        if error:
            return Response({"detail": error}, status=400)
        try:
            for field, value in payload.items():
                setattr(tag, field, value)
            tag.save()
        except Exception:
            return Response({"detail": "A product tag with this name or slug already exists."}, status=400)
        return Response(serialize_product_tag(tag))

    def delete(self, request, tag_id):
        deleted, _ = ProductTag.objects.filter(pk=tag_id).delete()
        if not deleted:
            return Response({"detail": "Product tag not found."}, status=404)
        return Response(status=204)
