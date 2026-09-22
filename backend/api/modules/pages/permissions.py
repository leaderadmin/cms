PAGE_READ = "page.read"
PAGE_CREATE = "page.create"
PAGE_UPDATE = "page.update"
PAGE_DELETE = "page.delete"
COMPONENT_READ = "page.component.read"
COMPONENT_CREATE = "page.component.create"
COMPONENT_UPDATE = "page.component.update"
COMPONENT_DELETE = "page.component.delete"

DECLARED_PERMISSIONS = (
    {"code": PAGE_READ, "module": "pages", "route": "GET /api/pages/"},
    {"code": PAGE_CREATE, "module": "pages", "route": "POST /api/pages/"},
    {"code": PAGE_UPDATE, "module": "pages", "route": "PATCH /api/pages/<id>/"},
    {"code": PAGE_DELETE, "module": "pages", "route": "DELETE /api/pages/<id>/"},
    {"code": COMPONENT_READ, "module": "pages", "route": "GET /api/pages/components/"},
    {"code": COMPONENT_CREATE, "module": "pages", "route": "POST /api/pages/components/"},
    {"code": COMPONENT_UPDATE, "module": "pages", "route": "PATCH /api/pages/components/<id>/"},
    {"code": COMPONENT_DELETE, "module": "pages", "route": "DELETE /api/pages/components/<id>/"},
)
