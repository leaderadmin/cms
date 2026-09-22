ARTICLE_READ = "article.read"
ARTICLE_CREATE = "article.create"
ARTICLE_UPDATE = "article.update"
ARTICLE_DELETE = "article.delete"
ARTICLE_PUBLISH = "article.publish"
CATEGORY_READ = "article.category.read"
CATEGORY_CREATE = "article.category.create"
CATEGORY_UPDATE = "article.category.update"
CATEGORY_DELETE = "article.category.delete"
TAG_READ = "article.tag.read"
TAG_CREATE = "article.tag.create"
TAG_UPDATE = "article.tag.update"
TAG_DELETE = "article.tag.delete"


DECLARED_PERMISSIONS = (
    {"code": ARTICLE_READ, "module": "articles", "route": "GET /api/articles/"},
    {"code": ARTICLE_CREATE, "module": "articles", "route": "POST /api/articles/"},
    {"code": ARTICLE_UPDATE, "module": "articles", "route": "PATCH /api/articles/<id>/"},
    {"code": ARTICLE_DELETE, "module": "articles", "route": "DELETE /api/articles/<id>/"},
    {"code": ARTICLE_PUBLISH, "module": "articles", "route": "POST /api/articles/<id>/publish/"},
    {"code": CATEGORY_READ, "module": "articles", "route": "GET /api/articles/categories/"},
    {"code": CATEGORY_CREATE, "module": "articles", "route": "POST /api/articles/categories/"},
    {"code": CATEGORY_UPDATE, "module": "articles", "route": "PATCH /api/articles/categories/<id>/"},
    {"code": CATEGORY_DELETE, "module": "articles", "route": "DELETE /api/articles/categories/<id>/"},
    {"code": TAG_READ, "module": "articles", "route": "GET /api/articles/tags/"},
    {"code": TAG_CREATE, "module": "articles", "route": "POST /api/articles/tags/"},
    {"code": TAG_UPDATE, "module": "articles", "route": "PATCH /api/articles/tags/<id>/"},
    {"code": TAG_DELETE, "module": "articles", "route": "DELETE /api/articles/tags/<id>/"},
)