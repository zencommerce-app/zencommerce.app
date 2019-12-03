"""
Periodic tasks:
 - Sync orders / purchases
 -

https://devcenter.heroku.com/articles/clock-processes-python
"""

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=30)
def sync_orders_job():
    print('This job is run every 30 minutes.')

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
