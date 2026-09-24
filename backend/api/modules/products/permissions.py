PRODUCT_READ = "product.read"
PRODUCT_CREATE = "product.create"
PRODUCT_UPDATE = "product.update"
PRODUCT_DELETE = "product.delete"
PRODUCT_PUBLISH = "product.publish"
PRODUCT_METADATA_READ = "product.metadata.read"
PRODUCT_METADATA_CREATE = "product.metadata.create"
PRODUCT_TAG_READ = "product.tag.read"
PRODUCT_TAG_CREATE = "product.tag.create"
PRODUCT_TAG_UPDATE = "product.tag.update"
PRODUCT_TAG_DELETE = "product.tag.delete"

DECLARED_PERMISSIONS = (
    {"code": PRODUCT_READ, "module": "products", "route": "GET /api/products/"},
    {"code": PRODUCT_CREATE, "module": "products", "route": "POST /api/products/"},
    {"code": PRODUCT_UPDATE, "module": "products", "route": "PATCH /api/products/<id>/"},
    {"code": PRODUCT_DELETE, "module": "products", "route": "DELETE /api/products/<id>/"},
    {"code": PRODUCT_PUBLISH, "module": "products", "route": "POST /api/products/<id>/publish/"},
    {"code": PRODUCT_METADATA_READ, "module": "products", "route": "GET /api/products/metadata/"},
    {"code": PRODUCT_METADATA_CREATE, "module": "products", "route": "POST /api/products/metadata/"},
    {"code": PRODUCT_TAG_READ, "module": "products", "route": "GET /api/products/tags/"},
    {"code": PRODUCT_TAG_CREATE, "module": "products", "route": "POST /api/products/tags/"},
    {"code": PRODUCT_TAG_UPDATE, "module": "products", "route": "PATCH /api/products/tags/<id>/"},
    {"code": PRODUCT_TAG_DELETE, "module": "products", "route": "DELETE /api/products/tags/<id>/"},
)
