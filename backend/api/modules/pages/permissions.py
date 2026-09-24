PAGE_READ = "page.read"
PAGE_CREATE = "page.create"
PAGE_UPDATE = "page.update"
PAGE_DELETE = "page.delete"
COMPONENT_READ = "page.component.read"
COMPONENT_CREATE = "page.component.create"
COMPONENT_UPDATE = "page.component.update"
COMPONENT_DELETE = "page.component.delete"
FORM_READ = "page.form.read"
FORM_CREATE = "page.form.create"
FORM_UPDATE = "page.form.update"
FORM_DELETE = "page.form.delete"

DECLARED_PERMISSIONS = (
    {"code": PAGE_READ, "module": "pages", "route": "GET /api/pages/"},
    {"code": PAGE_CREATE, "module": "pages", "route": "POST /api/pages/"},
    {"code": PAGE_UPDATE, "module": "pages", "route": "PATCH /api/pages/<id>/"},
    {"code": PAGE_DELETE, "module": "pages", "route": "DELETE /api/pages/<id>/"},
    {"code": COMPONENT_READ, "module": "pages", "route": "GET /api/pages/components/"},
    {"code": COMPONENT_CREATE, "module": "pages", "route": "POST /api/pages/components/"},
    {"code": COMPONENT_UPDATE, "module": "pages", "route": "PATCH /api/pages/components/<id>/"},
    {"code": COMPONENT_DELETE, "module": "pages", "route": "DELETE /api/pages/components/<id>/"},
    {"code": FORM_READ, "module": "pages", "route": "GET /api/pages/forms/"},
    {"code": FORM_CREATE, "module": "pages", "route": "POST /api/pages/forms/"},
    {"code": FORM_UPDATE, "module": "pages", "route": "PATCH /api/pages/forms/<id>/"},
    {"code": FORM_DELETE, "module": "pages", "route": "DELETE /api/pages/forms/<id>/"},
)
