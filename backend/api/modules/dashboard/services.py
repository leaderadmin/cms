import redis
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from ...models import Article, ActivityLog, FAQQuestion, Page, Product, RecruitmentJob
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
        today = timezone.localdate()
        daily_key = f"demo:visits:{today.isoformat()}"
        client.incr(daily_key)
        client.expire(daily_key, 60 * 60 * 24 * 31)
        start_date = today - timedelta(days=6)
        visits_by_day = [
            {"date": (start_date + timedelta(days=offset)).isoformat(), "visits": int(client.get(f"demo:visits:{(start_date + timedelta(days=offset)).isoformat()}") or 0)}
            for offset in range(7)
        ]
        activity_by_day = []
        for offset in range(7):
            date = start_date + timedelta(days=offset)
            activity_by_day.append({
                "date": date.isoformat(),
                "count": ActivityLog.objects.filter(created_at__date=date).count(),
            })
        return {
            "visits": client.incr("demo:visits"),
            "last_job": client.get("cron:last_run"),
            "visits_by_day": visits_by_day,
            "activity_by_day": activity_by_day,
            "content_counts": {
                "users": User.objects.filter(is_active=True).count(),
                "articles": Article.objects.count(),
                "pages": Page.objects.count(),
                "products": Product.objects.count(),
                "recruitment_jobs": RecruitmentJob.objects.count(),
                "faqs": FAQQuestion.objects.count(),
            },
        }


_dashboard_service = DashboardService()
