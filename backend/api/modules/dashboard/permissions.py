# Every dashboard route permission is declared here and referenced by its view.
DASHBOARD_STATS = "dashboard.stats.read"

DECLARED_PERMISSIONS = (
    {
        "code": DASHBOARD_STATS,
        "module": "dashboard",
        "route": "GET /api/stats/",
    },
)