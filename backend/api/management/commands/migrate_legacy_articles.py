from datetime import datetime

import pymysql
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import Article, ArticleCategory, ArticleCategoryTranslation, ArticleTranslation


def to_datetime(value):
    if value is None or timezone.is_aware(value):
        return value
    return timezone.make_aware(value, timezone.get_current_timezone())


class Command(BaseCommand):
    help = "Import legacy MySQL articles, categories, and translations into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="host.docker.internal")
        parser.add_argument("--port", type=int, default=3308)
        parser.add_argument("--user", default="abbank")
        parser.add_argument("--password", default="")
        parser.add_argument("--database", default="abbank")
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        connection = pymysql.connect(
            host=options["host"],
            port=options["port"],
            user=options["user"],
            password=options["password"],
            database=options["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            read_timeout=30,
        )
        try:
            with connection.cursor() as cursor:
                categories = self.fetch(cursor, "SELECT * FROM category ORDER BY ordering, id")
                category_translations = self.fetch(cursor, "SELECT * FROM category_translation ORDER BY id")
                articles_query = "SELECT * FROM article ORDER BY creation_date, id"
                if options["limit"]:
                    articles_query += " LIMIT %s" % int(options["limit"])
                articles = self.fetch(cursor, articles_query)
                article_ids = [row["id"] for row in articles]
                translations = []
                category_links = []
                if article_ids:
                    placeholders = ",".join(["%s"] * len(article_ids))
                    translations = self.fetch(cursor, f"SELECT * FROM article_translation WHERE article_id IN ({placeholders}) ORDER BY id", article_ids)
                    category_links = self.fetch(cursor, f"SELECT * FROM article_category WHERE article_id IN ({placeholders})", article_ids)
        finally:
            connection.close()

        counts = {"categories": len(categories), "category_translations": len(category_translations), "articles": len(articles), "translations": len(translations), "category_links": len(category_links)}
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Dry run: {counts}"))
            return

        with transaction.atomic():
            category_map = self.import_categories(categories)
            self.import_category_translations(category_translations, category_map)
            article_map = self.import_articles(articles)
            self.import_translations(translations, article_map)
            self.import_category_links(category_links, article_map, category_map)
        self.stdout.write(self.style.SUCCESS(f"Imported: {counts}"))

    @staticmethod
    def fetch(cursor, query, params=()):
        cursor.execute(query, params)
        return cursor.fetchall()

    def import_categories(self, rows):
        category_map = {}
        for row in rows:
            category, _ = ArticleCategory.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "name": row.get("name") or row["id"],
                    "category_type": row.get("type") or "article",
                    "status": row.get("status") if row.get("status") is not None else 1,
                    "ordering": row.get("ordering") or 0,
                    "created_at": to_datetime(row.get("creation_date")),
                    "updated_at": to_datetime(row.get("modification_date")),
                },
            )
            category_map[row["id"]] = category
        for row in rows:
            if row.get("parent_id") and row["id"] in category_map and row["parent_id"] in category_map:
                category_map[row["id"]].parent = category_map[row["parent_id"]]
                category_map[row["id"]].save(update_fields=["parent"])
        return category_map

    def import_category_translations(self, rows, category_map):
        for row in rows:
            category = category_map.get(row.get("category_id"))
            if not category or not row.get("language_code"):
                continue
            ArticleCategoryTranslation.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "category": category,
                    "language_code": row["language_code"],
                    "title": row.get("title") or row.get("raw_title") or category.name,
                    "description": row.get("description") or row.get("raw_description") or "",
                    "url_key": row.get("url_key") or "",
                    "status": row.get("status") if row.get("status") is not None else 1,
                    "meta_keyword": row.get("meta_keyword") or "",
                    "meta_description": row.get("meta_description") or "",
                    "created_at": to_datetime(row.get("creation_date")),
                    "updated_at": to_datetime(row.get("modification_date")),
                },
            )

    def import_articles(self, rows):
        article_map = {}
        for row in rows:
            article, _ = Article.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "name": row.get("name") or row["id"],
                    "article_type": row.get("type") or "article",
                    "status": row.get("status") if row.get("status") is not None else Article.STATUS_PENDING,
                    "view_count": row.get("view_count") or 0,
                    "ordering": row.get("ordering") or 0,
                    "legacy_author_id": row.get("author_id") or "",
                    "show_home": bool(row.get("show_home")),
                    "is_feature": bool(row.get("is_feature")),
                    "start_date": to_datetime(row.get("start_date")),
                    "end_date": to_datetime(row.get("end_date")),
                    "public_date": to_datetime(row.get("public_date")),
                    "legacy_image_id": row.get("article_image_id") or "",
                    "created_at": to_datetime(row.get("creation_date")),
                    "updated_at": to_datetime(row.get("modification_date")),
                },
            )
            article_map[row["id"]] = article
        return article_map

    def import_translations(self, rows, article_map):
        for row in rows:
            article = article_map.get(row.get("article_id"))
            if not article or not row.get("language_code"):
                continue
            ArticleTranslation.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "article": article,
                    "language_code": row["language_code"],
                    "title": row.get("title") or row.get("raw_title") or article.name,
                    "raw_title": row.get("raw_title") or "",
                    "sub_title": row.get("sub_title") or "",
                    "raw_sub_title": row.get("raw_sub_title") or "",
                    "content": row.get("content") or "",
                    "raw_content": row.get("raw_content") or "",
                    "short_description": row.get("short_description") or row.get("raw_short_description") or "",
                    "status": row.get("status") if row.get("status") is not None else article.status,
                    "public_date": to_datetime(row.get("public_date")),
                    "legacy_author_id": row.get("author_id") or "",
                    "legacy_feature_image_id": row.get("feature_image_id") or row.get("meta_image") or "",
                    "is_featured": bool(row.get("is_featured")),
                    "url_key": row.get("url_key") or row["id"],
                    "seo_title": row.get("seo_title") or "",
                    "seo_name": row.get("seo_name") or "",
                    "seo_content": row.get("seo_content") or "",
                    "meta_keyword": row.get("meta_keyword") or "",
                    "meta_description": row.get("meta_description") or "",
                    "created_at": to_datetime(row.get("creation_date")),
                    "updated_at": to_datetime(row.get("modification_date")),
                },
            )

    @staticmethod
    def import_category_links(rows, article_map, category_map):
        for row in rows:
            article = article_map.get(row.get("article_id"))
            category = category_map.get(row.get("category_id"))
            if article and category:
                article.categories.add(category)