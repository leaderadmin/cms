from django.db import migrations


PRODUCT_TYPES = (
    ("Thẻ", "the"),
    ("Khoản vay", "khoan-vay"),
    ("Tiết kiệm", "tiet-kiem"),
)

CATEGORIES = (
    ("Thẻ tín dụng", "the-tin-dung", "the"),
    ("Vay tiêu dùng", "vay-tieu-dung", "khoan-vay"),
    ("Tiết kiệm có kỳ hạn", "tiet-kiem-co-ky-han", "tiet-kiem"),
)

PRODUCTS = (
    {
        "name": "Thẻ tín dụng Everyday",
        "slug": "the-tin-dung-everyday",
        "kind": "card",
        "type_slug": "the",
        "category_slug": "the-tin-dung",
        "attributes": {
            "uu-dai-dac-biet-khac": "Hoàn tiền đến 5% cho chi tiêu thiết yếu.",
            "han-muc-giao-dich": "Tối đa 100.000.000 VNĐ",
            "tinh-nang-noi-bat": "Thanh toán không tiếp xúc và trả góp linh hoạt.",
            "phi-thuong-nien": "Miễn phí năm đầu",
            "lai-suat-nam": "33%/năm",
        },
        "vi": ("Thẻ tín dụng Everyday", "Chi tiêu thuận tiện với nhiều ưu đãi thiết thực.", "the-tin-dung-everyday"),
        "en": ("Everyday Credit Card", "Flexible spending with practical everyday benefits.", "everyday-credit-card"),
    },
    {
        "name": "Vay tiêu dùng linh hoạt",
        "slug": "vay-tieu-dung-linh-hoat",
        "kind": "loan",
        "type_slug": "khoan-vay",
        "category_slug": "vay-tieu-dung",
        "attributes": {
            "uu-dai-dac-biet-khac": "Hỗ trợ hồ sơ trực tuyến, giải ngân nhanh.",
            "han-muc-giao-dich": "Tối đa 500.000.000 VNĐ",
            "tinh-nang-noi-bat": "Thời hạn vay linh hoạt đến 60 tháng.",
            "phi-thuong-nien": "Không áp dụng",
            "lai-suat-nam": "Từ 12%/năm",
        },
        "vi": ("Vay tiêu dùng linh hoạt", "Giải pháp tài chính cho các kế hoạch cá nhân.", "vay-tieu-dung-linh-hoat"),
        "en": ("Flexible Personal Loan", "A flexible financing solution for personal plans.", "flexible-personal-loan"),
    },
    {
        "name": "Tiết kiệm An tâm",
        "slug": "tiet-kiem-an-tam",
        "kind": "saving",
        "type_slug": "tiet-kiem",
        "category_slug": "tiet-kiem-co-ky-han",
        "attributes": {
            "uu-dai-dac-biet-khac": "Tặng thêm lãi suất khi gửi trực tuyến.",
            "han-muc-giao-dich": "Từ 1.000.000 VNĐ",
            "tinh-nang-noi-bat": "Chủ động chọn kỳ hạn và phương thức nhận lãi.",
            "phi-thuong-nien": "Không áp dụng",
            "lai-suat-nam": "Lên đến 6,2%/năm",
        },
        "vi": ("Tiết kiệm An tâm", "Tích lũy an toàn với lãi suất hấp dẫn.", "tiet-kiem-an-tam"),
        "en": ("Peaceful Savings", "Build your savings securely with an attractive interest rate.", "peaceful-savings"),
    },
)


def seed_product_demo_data(apps, schema_editor):
    ProductType = apps.get_model("api", "ProductType")
    ProductCategory = apps.get_model("api", "ProductCategory")
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")
    Product = apps.get_model("api", "Product")
    ProductTranslation = apps.get_model("api", "ProductTranslation")

    types = {}
    for ordering, (name, slug) in enumerate(PRODUCT_TYPES):
        types[slug], _ = ProductType.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "status": 1, "ordering": ordering},
        )

    categories = {}
    for ordering, (name, slug, type_slug) in enumerate(CATEGORIES):
        categories[slug], _ = ProductCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "product_type": types[type_slug], "status": 1, "ordering": ordering},
        )

    attribute_set = ProductAttributeSet.objects.get(slug="thong-tin-san-pham")
    for ordering, item in enumerate(PRODUCTS):
        product, _ = Product.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "kind": item["kind"],
                "product_type": types[item["type_slug"]],
                "category": categories[item["category_slug"]],
                "attribute_set": attribute_set,
                "status": 1,
                "ordering": ordering,
                "is_featured": ordering == 0,
                "attributes": item["attributes"],
            },
        )
        for language_code, (title, short_description, url_key) in (("vi", item["vi"]), ("en", item["en"])):
            ProductTranslation.objects.get_or_create(
                product=product,
                language_code=language_code,
                defaults={
                    "title": title,
                    "short_description": short_description,
                    "content": short_description,
                    "url_key": url_key,
                    "seo_title": title,
                    "meta_description": short_description,
                    "status": 1,
                },
            )


def remove_product_demo_data(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    ProductCategory = apps.get_model("api", "ProductCategory")
    ProductType = apps.get_model("api", "ProductType")
    Product.objects.filter(slug__in=[item["slug"] for item in PRODUCTS]).delete()
    ProductCategory.objects.filter(slug__in=[item[1] for item in CATEGORIES]).delete()
    ProductType.objects.filter(slug__in=[item[1] for item in PRODUCT_TYPES]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0036_seed_product_attributes")]

    operations = [migrations.RunPython(seed_product_demo_data, remove_product_demo_data)]