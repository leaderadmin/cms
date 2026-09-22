import redis

from .redis_repository import get_redis_client


class DashboardService:
    def get_health(self):
        client = get_redis_client()
        try:
            client.ping()
            return "ok"
        except redis.RedisError:
            return "unavailable"

    def get_stats(self):
        client = get_redis_client()
        return {
            "visits": client.incr("demo:visits"),
            "last_job": client.get("cron:last_run"),
        }


_dashboard_service = DashboardService()
