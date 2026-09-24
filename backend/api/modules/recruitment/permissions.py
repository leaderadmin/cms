RECRUITMENT_READ = "recruitment.read"
RECRUITMENT_CREATE = "recruitment.create"
RECRUITMENT_UPDATE = "recruitment.update"
RECRUITMENT_DELETE = "recruitment.delete"
RECRUITMENT_DEPARTMENT_READ = "recruitment.department.read"
RECRUITMENT_DEPARTMENT_CREATE = "recruitment.department.create"
RECRUITMENT_DEPARTMENT_UPDATE = "recruitment.department.update"
RECRUITMENT_DEPARTMENT_DELETE = "recruitment.department.delete"

DECLARED_PERMISSIONS = (
    {"code": RECRUITMENT_READ, "module": "recruitment", "route": "GET /api/recruitment/"},
    {"code": RECRUITMENT_CREATE, "module": "recruitment", "route": "POST /api/recruitment/"},
    {"code": RECRUITMENT_UPDATE, "module": "recruitment", "route": "PATCH /api/recruitment/<id>/"},
    {"code": RECRUITMENT_DELETE, "module": "recruitment", "route": "DELETE /api/recruitment/<id>/"},
    {"code": RECRUITMENT_DEPARTMENT_READ, "module": "recruitment", "route": "GET /api/recruitment/departments/"},
    {"code": RECRUITMENT_DEPARTMENT_CREATE, "module": "recruitment", "route": "POST /api/recruitment/departments/"},
    {"code": RECRUITMENT_DEPARTMENT_UPDATE, "module": "recruitment", "route": "PATCH /api/recruitment/departments/<id>/"},
    {"code": RECRUITMENT_DEPARTMENT_DELETE, "module": "recruitment", "route": "DELETE /api/recruitment/departments/<id>/"},
)