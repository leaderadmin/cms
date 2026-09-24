FAQ_READ = "faq.read"
FAQ_CREATE = "faq.create"
FAQ_UPDATE = "faq.update"
FAQ_DELETE = "faq.delete"
DECLARED_PERMISSIONS = tuple({"code": f"faq.{action}", "module": "faq", "route": f"{method} /api/faq/"} for action, method in (("read", "GET"), ("create", "POST"), ("update", "PATCH"), ("delete", "DELETE")))