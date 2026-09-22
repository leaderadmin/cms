ENTITY_READ = "entity.read"
ENTITY_CREATE = "entity.create"
ENTITY_UPDATE = "entity.update"
ENTITY_DELETE = "entity.delete"

DECLARED_PERMISSIONS = (
    {"code": ENTITY_READ, "module": "entity", "route": "GET /api/entities/"},
    {"code": ENTITY_CREATE, "module": "entity", "route": "POST /api/entities/"},
    {"code": ENTITY_UPDATE, "module": "entity", "route": "PATCH /api/entities/<id>/"},
    {"code": ENTITY_DELETE, "module": "entity", "route": "DELETE /api/entities/<id>/"},
)