DEALER_READ = "dealer.read"
DEALER_CREATE = "dealer.create"
DEALER_UPDATE = "dealer.update"
DEALER_DELETE = "dealer.delete"
DECLARED_PERMISSIONS = tuple({"code": f"dealer.{action}", "module": "dealers", "route": f"{method} /api/dealers/"} for action, method in (("read", "GET"), ("create", "POST"), ("update", "PATCH"), ("delete", "DELETE")))