from collections import defaultdict
from datetime import datetime

import pymysql
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from api.models import (
    Dealer,
    FAQCategory,
    FAQQuestion,
    RecruitmentArea,
    RecruitmentJob,
    RecruitmentRegion,
    ProductAttribute,
    ProductAttributeSet,
    Product,
    ProductTranslation,
    ProductGroup,
    ProductType,
)


def aware(value):
    if value is None or timezone.is_aware(value):
        return value
    return timezone.make_aware(value, timezone.get_current_timezone())


def decimal_or_none(value, minimum, maximum):
    try:
        number = float(value) if value not in (None, "") else None
        return number if number is not None and minimum <= number <= maximum else None
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Import legacy CMS FAQ, recruitment, region, area, and dealer data into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="host.docker.internal")
        parser.add_argument("--port", type=int, default=3308)
        parser.add_argument("--user", default="abbank")
        parser.add_argument("--password", default="")
        parser.add_argument("--database", default="abbank")
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
            read_timeout=60,
        )
        try:
            with connection.cursor() as cursor:
                data = {
                    "regions": self.fetch(cursor, "SELECT * FROM location_area ORDER BY id"),
                    "areas": self.fetch(cursor, "SELECT * FROM province ORDER BY id"),
                    "dealers": self.fetch(cursor, "SELECT * FROM dealer ORDER BY id"),
                    "dealer_translations": self.fetch(cursor, "SELECT * FROM dealer_translation ORDER BY id"),
                    "faq_types": self.fetch(cursor, "SELECT * FROM faq_type ORDER BY id"),
                    "faq_type_translations": self.fetch(cursor, "SELECT * FROM faq_type_translation ORDER BY id"),
                    "faqs": self.fetch(cursor, "SELECT * FROM faq ORDER BY ordering, id"),
                    "faq_translations": self.fetch(cursor, "SELECT * FROM faq_translation ORDER BY id"),
                    "jobs": self.fetch(cursor, "SELECT * FROM career ORDER BY creation_date, id"),
                    "job_translations": self.fetch(cursor, "SELECT * FROM career_translation ORDER BY id"),
                    "job_types": self.fetch(cursor, "SELECT * FROM job ORDER BY id"),
                    "attributes": self.fetch(cursor, "SELECT * FROM attribute ORDER BY id"),
                    "attribute_sets": self.fetch(cursor, "SELECT * FROM attribute_set ORDER BY id"),
                    "attribute_links": self.fetch(cursor, "SELECT * FROM attribute_attribute_set ORDER BY attribute_set_id, attribute_id"),
                    "attribute_translations": self.fetch(cursor, "SELECT * FROM attribute_translation ORDER BY id"),
                    "services": self.fetch(cursor, "SELECT * FROM service ORDER BY id"),
                    "service_translations": self.fetch(cursor, "SELECT * FROM service_translation ORDER BY id"),
                    "loans": self.fetch(cursor, "SELECT * FROM loan ORDER BY id"),
                    "loan_translations": self.fetch(cursor, "SELECT * FROM loan_translation ORDER BY id"),
                    "savings": self.fetch(cursor, "SELECT * FROM saving ORDER BY id"),
                    "saving_translations": self.fetch(cursor, "SELECT * FROM saving_translation ORDER BY id"),
                    "cards": self.fetch(cursor, "SELECT * FROM type_card ORDER BY id"),
                    "card_translations": self.fetch(cursor, "SELECT * FROM type_card_translation ORDER BY id"),
                    "promotions": self.fetch(cursor, "SELECT * FROM promotion ORDER BY id"),
                    "promotion_translations": self.fetch(cursor, "SELECT * FROM promotion_translation ORDER BY id"),
                }
        finally:
            connection.close()

        counts = {key: len(value) for key, value in data.items()}
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Dry run: {counts}"))
            return

        with transaction.atomic():
            regions = self.import_regions(data["regions"])
            areas = self.import_areas(data["areas"], regions)
            self.import_dealers(data["dealers"], data["dealer_translations"], areas)
            categories = self.import_faq_categories(data["faq_types"], data["faq_type_translations"])
            self.import_faqs(data["faqs"], data["faq_translations"], categories)
            self.import_jobs(data["jobs"], data["job_translations"], data["job_types"], regions, areas)
            self.import_attributes(
                data["attributes"], data["attribute_sets"], data["attribute_links"], data["attribute_translations"]
            )
            self.import_products(data)
            self.sync_product_hierarchy()
        self.stdout.write(self.style.SUCCESS(f"Imported: {counts}"))

    @staticmethod
    def fetch(cursor, query):
        cursor.execute(query)
        return cursor.fetchall()

    def import_regions(self, rows):
        regions = {}
        for row in rows:
            name = (row.get("title") or row.get("code") or row["id"]).strip()
            region = RecruitmentRegion.objects.filter(legacy_id=str(row["id"])).first()
            if region is None:
                region = RecruitmentRegion.objects.filter(slug=f"legacy-region-{row['id']}").first()
            if region is None:
                region = RecruitmentRegion.objects.filter(name=name).first()
            if region is None:
                region = RecruitmentRegion(slug=f"legacy-region-{row['id']}")
            region.name = name
            region.legacy_id = str(row["id"])
            region.status = row.get("status") if row.get("status") is not None else 1
            region.save()
            regions[str(row["id"])] = region
        return regions

    def import_areas(self, rows, regions):
        areas = {}
        fallback_region = next(iter(regions.values()), None)
        for row in rows:
            region = regions.get(str(row.get("location_area_id"))) or fallback_region
            name = (row.get("name") or row.get("code") or row["id"]).strip()
            area = RecruitmentArea.objects.filter(legacy_id=str(row["id"])).first()
            if area is None:
                area = RecruitmentArea.objects.filter(region=region, name=name).first()
            if area is None:
                area = RecruitmentArea(region=region, name=name, slug=f"legacy-area-{row['id']}")
            area.region = region
            area.name = name
            area.legacy_id = str(row["id"])
            area.slug = f"legacy-area-{row['id']}"
            area.status = row.get("status") if row.get("status") is not None else 1
            area.save()
            areas[str(row["id"])] = area
        return areas

    def import_dealers(self, rows, translations, areas):
        translated = defaultdict(list)
        for row in translations:
            translated[str(row.get("dealer_id"))].append(row)
        for row in rows:
            options = translated[str(row["id"])]
            vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
            code = f"legacy-{row['id']}"
            dealer = Dealer.objects.filter(legacy_id=str(row["id"])).first()
            if dealer is None:
                dealer = Dealer.objects.filter(code=code).first()
            dealer.legacy_id = str(row["id"])
            dealer.code = code
            dealer.dealer_type = {
                "dealer": Dealer.TYPE_BRANCH,
                "atm": Dealer.TYPE_ATM,
                "transaction-office": Dealer.TYPE_TRANSACTION_OFFICE,
            }.get(str(row.get("functional") or "").strip().lower(), Dealer.TYPE_BRANCH)
            dealer.name = vi.get("name") or row.get("name") or code
            dealer.area = areas.get(str(row.get("province_id")))
            province = areas.get(str(row.get("province_id")))
            dealer.province_city = province.name if province else (row.get("province_id") or "")
            dealer.address = vi.get("address") or row.get("address") or ""
            dealer.hotline = vi.get("phone") or row.get("phone") or ""
            dealer.email = row.get("email") or row.get("card_email") or ""
            dealer.latitude = decimal_or_none(row.get("latitude"), -90, 90)
            dealer.longitude = decimal_or_none(row.get("longitude"), -180, 180)
            dealer.opening_hours = vi.get("timework") or row.get("opening_hours") or ""
            dealer.status = row.get("status") if row.get("status") is not None else 1
            dealer.created_at = aware(row.get("creation_date")) or dealer.created_at
            dealer.updated_at = aware(row.get("modification_date")) or dealer.updated_at
            dealer.save()

    def import_faq_categories(self, rows, translations):
        translated = defaultdict(list)
        for row in translations:
            translated[str(row.get("faq_type_id"))].append(row)
        categories = {}
        for row in rows:
            options = translated[str(row["id"])]
            vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
            name = vi.get("name") or row.get("name") or row["id"]
            category = FAQCategory.objects.filter(legacy_id=str(row["id"])).first()
            if category is None:
                category = FAQCategory.objects.filter(slug=f"legacy-faq-category-{row['id']}").first()
            if category is None:
                category = FAQCategory(legacy_id=str(row["id"]), slug=f"legacy-faq-category-{row['id']}")
            category.legacy_id = str(row["id"])
            category.name = name
            category.ordering = row.get("ordering") or 0
            category.status = row.get("status") if row.get("status") is not None else 1
            category.created_at = aware(row.get("creation_date")) or category.created_at
            category.updated_at = aware(row.get("modification_date")) or category.updated_at
            category.save()
            categories[str(row["id"])] = category
        return categories

    def import_faqs(self, rows, translations, categories):
        translated = defaultdict(list)
        for row in translations:
            translated[str(row.get("faq_id"))].append(row)
        for row in rows:
            category = categories.get(str(row.get("faq_type_id")))
            if not category:
                continue
            options = translated[str(row["id"])]
            vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
            en = next((item for item in options if item.get("language_code") == "en"), {})
            question_vi = vi.get("question") or row.get("name") or row["id"]
            question = FAQQuestion.objects.filter(legacy_id=str(row["id"])).first()
            if not question:
                question = FAQQuestion.objects.filter(
                    legacy_id__isnull=True, category=category, question_vi=question_vi
                ).first()
            if not question:
                question = FAQQuestion(legacy_id=str(row["id"]), category=category, question_vi=question_vi)
            question.category = category
            question.answer_vi = vi.get("answer") or ""
            question.question_en = en.get("question") or ""
            question.answer_en = en.get("answer") or ""
            question.ordering = row.get("ordering") or 0
            question.status = row.get("status") if row.get("status") is not None else 1
            question.created_at = aware(row.get("creation_date")) or question.created_at
            question.updated_at = aware(row.get("modification_date")) or question.updated_at
            question.save()

    def import_jobs(self, rows, translations, job_types, regions, areas):
        translated = defaultdict(list)
        for row in translations:
            translated[str(row.get("career_id"))].append(row)
        type_names = {str(row["id"]): row.get("name") or "" for row in job_types}
        for row in rows:
            options = translated[str(row["id"])]
            vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
            title = vi.get("title") or row.get("name") or row["id"]
            slug = f"legacy-career-{row['id']}"
            province_id = str(row.get("province_id")) if row.get("province_id") is not None else ""
            area = areas.get(province_id)
            region = area.region if area else None
            status = RecruitmentJob.STATUS_PUBLISHED if row.get("status") == 1 else RecruitmentJob.STATUS_DRAFT
            job = RecruitmentJob.objects.filter(legacy_id=str(row["id"])).first()
            if job is None:
                job = RecruitmentJob.objects.filter(slug=slug).first()
            if job is None:
                job = RecruitmentJob(legacy_id=str(row["id"]), slug=slug)
            job.legacy_id = str(row["id"])
            job.title = title
            job.department = type_names.get(str(row.get("job_id")), "")
            job.region = region
            job.area = area
            job.location = title
            job.employment_type = row.get("working_time") or ""
            job.description = vi.get("content") or ""
            job.requirements = vi.get("requirements") or ""
            job.deadline = row.get("expired_date")
            job.status = status
            job.created_at = aware(row.get("creation_date")) or job.created_at
            job.updated_at = aware(row.get("modification_date")) or job.updated_at
            job.save()

    def import_attributes(self, attributes, attribute_sets, links, translations):
        translated = defaultdict(list)
        for row in translations:
            translated[str(row.get("attribute_id"))].append(row)
        imported_attributes = {}
        for row in attributes:
            options = translated[str(row["id"])]
            vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
            name = vi.get("name") or row.get("name") or row["id"]
            attribute, _ = ProductAttribute.objects.update_or_create(
                slug=f"legacy-attribute-{row['id']}",
                defaults={
                    "name": name,
                    "value_type": row.get("type") or "text",
                    "status": row.get("status") if row.get("status") is not None else 1,
                },
            )
            imported_attributes[str(row["id"])] = attribute

        imported_sets = {}
        for row in attribute_sets:
            attribute_set, _ = ProductAttributeSet.objects.update_or_create(
                slug=f"legacy-attribute-set-{row['id']}",
                defaults={
                    "name": row.get("name") or row["id"],
                    "status": row.get("status") if row.get("status") is not None else 1,
                },
            )
            imported_sets[str(row["id"])] = attribute_set

        grouped = defaultdict(list)
        for row in links:
            attribute = imported_attributes.get(str(row.get("attribute_id")))
            if attribute:
                grouped[str(row.get("attribute_set_id"))].append(attribute)
        for set_id, attribute_set in imported_sets.items():
            attribute_set.attributes.set(grouped[set_id])

    def import_products(self, data):
        domains = (
            ("service", data["services"], data["service_translations"], "service_id"),
            ("loan", data["loans"], data["loan_translations"], "loan_id"),
            ("saving", data["savings"], data["saving_translations"], "saving_id"),
            ("card", data["cards"], data["card_translations"], "type_card_id"),
            ("promotion", data["promotions"], data["promotion_translations"], "promotion_id"),
        )
        attribute_sets = {item.slug.removeprefix("legacy-attribute-set-"): item for item in ProductAttributeSet.objects.filter(slug__startswith="legacy-attribute-set-")}
        for kind, rows, translations, foreign_key in domains:
            translated = defaultdict(list)
            for translation in translations:
                translated[str(translation.get(foreign_key))].append(translation)
            for row in rows:
                source_id = str(row["id"])
                options = translated[source_id]
                vi = next((item for item in options if item.get("language_code") == "vi"), options[0] if options else {})
                name = vi.get("title") or vi.get("name") or row.get("title") or row.get("name") or source_id
                slug = f"legacy-{kind}-{source_id}"
                attribute_set = attribute_sets.get(str(row.get("attribute_set_id")))
                product, _ = Product.objects.update_or_create(
                    legacy_id=f"{kind}:{source_id}",
                    defaults={
                        "name": name,
                        "slug": slug,
                        "kind": kind,
                        "attribute_set": attribute_set,
                        "status": Product.STATUS_ACTIVE if row.get("status") == 1 else Product.STATUS_DRAFT,
                        "ordering": row.get("ordering") or 0,
                        "is_featured": bool(row.get("is_feature")),
                        "extra_data": {"legacy_source": kind, "legacy_id": source_id},
                        "created_at": aware(row.get("creation_date")),
                        "updated_at": aware(row.get("modification_date")),
                    },
                )
                for translation in options:
                    language = translation.get("language_code") or "vi"
                    title = translation.get("title") or translation.get("name") or name
                    ProductTranslation.objects.update_or_create(
                        product=product,
                        language_code=language,
                        defaults={
                            "title": title,
                            "short_description": translation.get("short_description") or "",
                            "content": translation.get("content") or translation.get("description") or translation.get("banner") or "",
                            "url_key": translation.get("url_key") or translation.get("slug") or slug,
                            "meta_keyword": translation.get("meta_keyword") or "",
                            "meta_description": translation.get("meta_description") or "",
                            "status": Product.STATUS_ACTIVE if translation.get("status") == 1 else Product.STATUS_DRAFT,
                        },
                    )

    def sync_product_hierarchy(self):
        type_groups = {
            "card": ("the", "the-tin-dung", "thẻ tín dụng"),
            "loan": ("khoan-vay", "khoan-vay", "Khoản vay"),
            "saving": ("tiet-kiem", "tiet-kiem", "Tiết kiệm"),
            "service": ("dich-vu", "dich-vu", "Dịch vụ"),
            "promotion": ("uu-dai", "uu-dai", "Ưu đãi"),
        }
        types = {item.slug: item for item in ProductType.objects.all()}
        for source_kind, (type_slug, group_slug, group_name) in type_groups.items():
            product_type = types.get(type_slug)
            if not product_type:
                continue
            ProductGroup.objects.update_or_create(
                slug=group_slug,
                defaults={
                    "name": group_name,
                    "product_type": product_type,
                    "status": 1,
                },
            )
            Product.objects.filter(kind=source_kind).update(kind=group_slug, product_type=product_type)
