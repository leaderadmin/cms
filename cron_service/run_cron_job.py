import json

from services import CronJobService


if __name__ == "__main__":
    print(json.dumps(CronJobService().run()))
