import json

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from afex_logger.log_service import AppLogService


@shared_task
def submit_log_data(log_type, log_data: str):
    if settings.DEBUG:
        print("Submitting log data", timezone.now(), ":", log_type, "|", log_data)
    try:
        data = json.loads(log_data)
        AppLogService().send_logs(log_type, data)
    except Exception as e:
        print(e)

