"""
⏰ Taskiq Scheduler Configuration

Redis broker 기반 태스크 스케줄러.
"""

import os

from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker, RedisScheduleSource

# Redis 연결 설정
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Broker 설정 (Redis List Queue)
broker = ListQueueBroker(url=REDIS_URL)

# 스케줄 소스 (Redis)
schedule_source = RedisScheduleSource(url=REDIS_URL)

# 스케줄러
scheduler = TaskiqScheduler(broker=broker, sources=[schedule_source])


# ========================================
# Task Registration
# ========================================


@broker.task
def crawl_prices_task():
    """전체 영양제 가격 수집 태스크"""
    from domains.features.prices.tasks import run_crawl_all_prices

    return run_crawl_all_prices()


@broker.task
def check_alerts_task():
    """가격 알림 체크 태스크"""
    from domains.features.prices.tasks import run_check_all_alerts

    return run_check_all_alerts()


# ========================================
# Scheduled Jobs (Cron)
# ========================================

# 스케줄 등록 예시 (실제로는 Redis에 저장)
SCHEDULES = {
    "crawl_prices_daily": {
        "task": "config.scheduler:crawl_prices_task",
        "cron": "0 6 * * *",  # 매일 오전 6시
        "description": "Daily price crawling",
    },
    "check_alerts_hourly": {
        "task": "config.scheduler:check_alerts_task",
        "cron": "0 * * * *",  # 매 정시
        "description": "Hourly price alert check",
    },
}


def setup_schedules():
    """스케줄 초기 설정 (앱 시작 시 호출)"""
    # TODO: Redis에 스케줄 등록
    pass
