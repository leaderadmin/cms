from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from ...models import Article, ArticleCategory, ArticleTranslation, MediaFile, Tag
from .permissions import ARTICLE_CREATE, ARTICLE_DELETE, ARTICLE_PUBLISH, ARTICLE_READ, ARTICLE_UPDATE, CATEGORY_CREATE, CATEGORY_DELETE, CATEGORY_READ, CATEGORY_UPDATE, TAG_CREATE, TAG_DELETE, TAG_READ, TAG_UPDATE
from .serializers import article_payload, category_payload, serialize_article, serialize_category, serialize_tag, tag_payload


class ArticleListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": ARTICLE_READ, "POST": ARTICLE_CREATE}

    def get(self, request):
        queryset = Article.objects.prefetch_related("translations", "categories__translations")
        query = request.query_params.get("q", "").strip()
        language_code = request.query_params.get("language", "").strip() or None
        status_value = request.query_params.get("status")
        article_type = request.query_params.get("type", "").strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(translations__title__icontains=query))
        if language_code:
            queryset = queryset.filter(translations__language_code=language_code)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if article_type:
            queryset = queryset.filter(article_type=article_type)
        queryset = queryset.distinct().order_by("-public_date", "-id")
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = min(100, max(1, int(request.query_params.get("page_size", 25))))
        except (TypeError, ValueError):
            page_size = 25
        total = queryset.count()
        start = (page - 1) * page_size
        articles = queryset[start:start + page_size]
        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "next": page + 1 if start + page_size < total else None,
            "previous": page - 1 if page > 1 and start < total else None,
            "results": [serialize_article(article, language_code) for article in articles],
        })

    def post(self, request):
        payload, error = article_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        categories = ArticleCategory.objects.filter(id__in=payload["category_ids"])
        if len(categories) != len(set(payload["category_ids"])):
            return Response({"detail": "One or more categories were not found."}, status=400)
        image = None
        if payload["image_id"]:
            image = MediaFile.objects.filter(pk=payload["image_id"], content_type__startswith="image/").first()
            if not image:
                return Response({"detail": "Selected thumbnail was not found."}, status=400)
        with transaction.atomic():
            article = Article.objects.create(
                name=payload["name"], article_type=payload["article_type"], status=payload["status"],
                ordering=payload["ordering"], show_home=payload["show_home"], is_feature=payload["is_feature"],
                tags=payload["tags"],
                image=image,
                cta_label=payload["cta"]["label"], cta_url=payload["cta"]["url"], cta_phone=payload["cta"]["phone"],
            )
            article.categories.set(categories)
            article.managed_tags.set(Tag.objects.filter(id__in=payload["tag_ids"]))
            for translation in payload["translations"]:
                ArticleTranslation.objects.create(article=article, **translation)
        return Response(serialize_article(article, payload["translation"]["language_code"]), status=201)


class ArticleDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": ARTICLE_READ, "PATCH": ARTICLE_UPDATE, "DELETE": ARTICLE_DELETE}

    def get(self, request, article_id):
        try:
            article = Article.objects.prefetch_related("translations", "categories__translations").get(pk=article_id)
        except Article.DoesNotExist:
            return Response({"detail": "Article not found."}, status=404)
        language_code = request.query_params.get("language", "").strip() or None
        return Response(serialize_article(article, language_code))

    def patch(self, request, article_id):
        try:
            article = Article.objects.prefetch_related("translations", "categories__translations").get(pk=article_id)
        except Article.DoesNotExist:
            return Response({"detail": "Article not found."}, status=404)
        payload, error = article_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        categories = ArticleCategory.objects.filter(id__in=payload["category_ids"])
        if len(categories) != len(set(payload["category_ids"])):
            return Response({"detail": "One or more categories were not found."}, status=400)
        image = None
        if payload["image_id"]:
            image = MediaFile.objects.filter(pk=payload["image_id"], content_type__startswith="image/").first()
            if not image:
                return Response({"detail": "Selected thumbnail was not found."}, status=400)
        language_code = payload["translation"]["language_code"]
        with transaction.atomic():
            article.name = payload["name"]
            article.article_type = payload["article_type"]
            article.status = payload["status"]
            article.ordering = payload["ordering"]
            article.show_home = payload["show_home"]
            article.is_feature = payload["is_feature"]
            article.tags = payload["tags"]
            article.image = image
            article.cta_label = payload["cta"]["label"]
            article.cta_url = payload["cta"]["url"]
            article.cta_phone = payload["cta"]["phone"]
            article.save()
            article.categories.set(categories)
            article.managed_tags.set(Tag.objects.filter(id__in=payload["tag_ids"]))
            ArticleTranslation.objects.update_or_create(
                article=article, language_code=language_code, defaults=payload["translation"]
            )
        article.refresh_from_db()
        return Response(serialize_article(article, language_code))

    def delete(self, request, article_id):
        updated = Article.objects.filter(pk=article_id).update(status=Article.STATUS_DELETED)
        if not updated:
            return Response({"detail": "Article not found."}, status=404)
        return Response(status=204)


class ArticlePublishView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = ARTICLE_PUBLISH

    def post(self, request, article_id):
        article = Article.objects.filter(pk=article_id).first()
        if not article:
            return Response({"detail": "Article not found."}, status=404)
        article.status = Article.STATUS_APPROVED
        article.save(update_fields=("status",))
        article.translations.update(status=Article.STATUS_APPROVED)
        return Response(serialize_article(article, request.data.get("language")))


class ArticleCategoryListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": CATEGORY_READ, "POST": CATEGORY_CREATE}

    def get(self, request):
        categories = ArticleCategory.objects.prefetch_related("translations").all()
        query = request.query_params.get("q", "").strip()
        status_value = request.query_params.get("status")
        category_type = request.query_params.get("type", "").strip()
        if query:
            categories = categories.filter(Q(name__icontains=query) | Q(translations__title__icontains=query))
        if status_value:
            categories = categories.filter(status=status_value)
        if category_type:
            categories = categories.filter(category_type=category_type)
        categories = categories.distinct()
        return Response([serialize_category(category) for category in categories])

    def post(self, request):
        payload, error = category_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        parent = ArticleCategory.objects.filter(pk=payload["parent_id"]).first() if payload["parent_id"] else None
        if payload["parent_id"] and not parent:
            return Response({"detail": "Parent category was not found."}, status=400)
        with transaction.atomic():
            category = ArticleCategory.objects.create(
                name=payload["name"], category_type=payload["category_type"], status=payload["status"],
                ordering=payload["ordering"], parent=parent,
            )
            category.translations.update_or_create(
                language_code=payload["translation"]["language_code"], defaults=payload["translation"]
            )
        return Response(serialize_category(category), status=201)


class ArticleCategoryDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": CATEGORY_READ, "PATCH": CATEGORY_UPDATE, "DELETE": CATEGORY_DELETE}

    def patch(self, request, category_id):
        category = ArticleCategory.objects.filter(pk=category_id).first()
        if not category:
            return Response({"detail": "Category not found."}, status=404)
        payload, error = category_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        if payload["parent_id"] == category.id:
            return Response({"detail": "A category cannot be its own parent."}, status=400)
        parent = ArticleCategory.objects.filter(pk=payload["parent_id"]).first() if payload["parent_id"] else None
        if payload["parent_id"] and not parent:
            return Response({"detail": "Parent category was not found."}, status=400)
        with transaction.atomic():
            category.name = payload["name"]
            category.category_type = payload["category_type"]
            category.status = payload["status"]
            category.ordering = payload["ordering"]
            category.parent = parent
            category.save()
            category.translations.update_or_create(
                language_code=payload["translation"]["language_code"], defaults=payload["translation"]
            )
        category.refresh_from_db()
        return Response(serialize_category(category))

    def delete(self, request, category_id):
        updated = ArticleCategory.objects.filter(pk=category_id).update(status=Article.STATUS_DELETED)
        if not updated:
            return Response({"detail": "Category not found."}, status=404)
        return Response(status=204)


class ArticleTagListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": TAG_READ, "POST": TAG_CREATE}

    def get(self, request):
        tags = Tag.objects.all()
        query = request.query_params.get("q", "").strip()
        if query:
            tags = tags.filter(Q(name__icontains=query) | Q(slug__icontains=query))
        return Response([serialize_tag(tag) for tag in tags])

    def post(self, request):
        payload, error = tag_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            tag = Tag.objects.create(**payload)
        except Exception:
            return Response({"detail": "A tag with this name or slug already exists."}, status=400)
        return Response(serialize_tag(tag), status=201)


class ArticleTagDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": TAG_READ, "PATCH": TAG_UPDATE, "DELETE": TAG_DELETE}

    def patch(self, request, tag_id):
        tag = Tag.objects.filter(pk=tag_id).first()
        if not tag:
            return Response({"detail": "Tag not found."}, status=404)
        payload, error = tag_payload(request.data, tag)
        if error:
            return Response({"detail": error}, status=400)
        try:
            for field, value in payload.items():
                setattr(tag, field, value)
            tag.save()
        except Exception:
            return Response({"detail": "A tag with this name or slug already exists."}, status=400)
        return Response(serialize_tag(tag))

    def delete(self, request, tag_id):
        deleted, _ = Tag.objects.filter(pk=tag_id).delete()
        if not deleted:
            return Response({"detail": "Tag not found."}, status=404)
        return Response(status=204)