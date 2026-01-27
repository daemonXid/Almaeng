"""
⏰ Taskiq Scheduler Configuration (Phase 2)

가격 모니터링 자동화는 Phase 2로 연기.
현재는 수동으로 Admin에서 관리.
"""

# Phase 2: Taskiq 기반 자동 가격 체크
# import os
# from taskiq import TaskiqScheduler
# from taskiq_redis import ListQueueBroker, RedisScheduleSource


# Phase 2: 가격 모니터링 자동화
# 
# @broker.task
# async def check_wishlist_prices_task():
#     """매일 오전 6시 자동 실행"""
#     from domains.wishlist.interface import check_price_drops
#     ...
#
# SCHEDULES = {
#     "check_wishlist_prices_daily": {
#         "task": "config.scheduler:check_wishlist_prices_task",
#         "cron": "0 6 * * *",
#     },
# }
