import json
from datetime import datetime, timezone

from redis_repository import get_redis_client


class CronJobService:
    def run(self):
        payload = {
            "ran_at": datetime.now(timezone.utc).isoformat(),
            "message": "Scheduled cron service job completed",
        }
        get_redis_client().set("cron:last_run", json.dumps(payload))
        return payload
