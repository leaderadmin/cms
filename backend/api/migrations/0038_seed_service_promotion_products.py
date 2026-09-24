from django.db import migrations


def seed_service_and_promotion(apps, schema_editor):
    ProductType = apps.get_model("api", "ProductType")
    ProductCategory = apps.get_model("api", "ProductCategory")
    ProductAttributeSet = apps.get_model("api", "ProductAttributeSet")
    Product = apps.get_model("api", "Product")
    ProductTranslation = apps.get_model("api", "ProductTranslation")

    service_type, _ = ProductType.objects.get_or_create(
        slug="dich-vu",
        defaults={"name": "Dịch vụ", "status": 1, "ordering": 3},
    )
    promotion_type, _ = ProductType.objects.get_or_create(
        slug="uu-dai",
        defaults={"name": "Ưu đãi", "status": 1, "ordering": 4},
    )
    service_category, _ = ProductCategory.objects.get_or_create(
        slug="dich-vu-ngan-hang",
        defaults={"name": "Dịch vụ ngân hàng", "product_type": service_type, "status": 1, "ordering": 3},
    )
    promotion_category, _ = ProductCategory.objects.get_or_create(
        slug="uu-dai-noi-bat",
        defaults={"name": "Ưu đãi nổi bật", "product_type": promotion_type, "status": 1, "ordering": 4},
    )
    attribute_set = ProductAttributeSet.objects.get(slug="thong-tin-san-pham")
    products = (
        {
            "name": "Internet Banking",
            "slug": "internet-banking",
            "kind": "service",
            "product_type": service_type,
            "category": service_category,
            "attributes": {
                "uu-dai-dac-biet-khac": "Miễn phí đăng ký và sử dụng cơ bản.",
                "han-muc-giao-dich": "Theo hạn mức tài khoản",
                "tinh-nang-noi-bat": "Chuyển tiền, thanh toán hóa đơn và quản lý tài khoản trực tuyến.",
                "phi-thuong-nien": "Miễn phí",
                "lai-suat-nam": "Không áp dụng",
            },
            "translations": (("vi", "Internet Banking", "Quản lý tài chính nhanh chóng trên nền tảng số.", "internet-banking"), ("en", "Internet Banking", "Manage your finances quickly through digital banking.", "internet-banking-en")),
        },
        {
            "name": "Ưu đãi hoàn tiền mùa hè",
            "slug": "uu-dai-hoan-tien-mua-he",
            "kind": "promotion",
            "product_type": promotion_type,
            "category": promotion_category,
            "attributes": {
                "uu-dai-dac-biet-khac": "Hoàn tiền 10% cho giao dịch đủ điều kiện.",
                "han-muc-giao-dich": "Tối đa 500.000 VNĐ/tháng",
                "tinh-nang-noi-bat": "Áp dụng cho khách hàng đăng ký mới.",
                "phi-thuong-nien": "Không áp dụng",
                "lai-suat-nam": "Không áp dụng",
            },
            "translations": (("vi", "Ưu đãi hoàn tiền mùa hè", "Tận hưởng ưu đãi hoàn tiền trong mùa hè này.", "uu-dai-hoan-tien-mua-he"), ("en", "Summer Cashback Offer", "Enjoy cashback benefits throughout the summer.", "summer-cashback-offer")),
        },
    )
    for ordering, item in enumerate(products, start=3):
        product, _ = Product.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "kind": item["kind"],
                "product_type": item["product_type"],
                "category": item["category"],
                "attribute_set": attribute_set,
                "status": 1,
                "ordering": ordering,
                "attributes": item["attributes"],
            },
        )
        for language_code, title, description, url_key in item["translations"]:
            ProductTranslation.objects.get_or_create(
                product=product,
                language_code=language_code,
                defaults={
                    "title": title,
                    "short_description": description,
                    "content": description,
                    "url_key": url_key,
                    "seo_title": title,
                    "meta_description": description,
                    "status": 1,
                },
            )


def remove_service_and_promotion(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    ProductCategory = apps.get_model("api", "ProductCategory")
    ProductType = apps.get_model("api", "ProductType")
    Product.objects.filter(slug__in=["internet-banking", "uu-dai-hoan-tien-mua-he"]).delete()
    ProductCategory.objects.filter(slug__in=["dich-vu-ngan-hang", "uu-dai-noi-bat"]).delete()
    ProductType.objects.filter(slug__in=["dich-vu", "uu-dai"]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0037_seed_product_demo_data")]

    operations = [migrations.RunPython(seed_service_and_promotion, remove_service_and_promotion)]