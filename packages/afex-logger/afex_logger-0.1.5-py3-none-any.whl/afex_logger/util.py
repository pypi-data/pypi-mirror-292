import decimal
import json
from datetime import datetime, date
from uuid import UUID

from django.conf import settings
from django.db.models import TextChoices

from afex_logger.log_service import AppLogService
from afex_logger.tasks import submit_log_data


class LogTypes(TextChoices):
    requests = "requests"
    process = "process"
    errors = "errors"
    activities = "activities"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        elif hasattr(o, '__dict__'):
            return o.__dict__.get('name', '')
        return super(DecimalEncoder, self).default(o)


class LogUtil:

    @classmethod
    def submit_error_log(cls, data):
        submit_log_data.delay(LogTypes.errors, json.dumps(data, cls=DecimalEncoder))

    @classmethod
    def submit_activity_log(cls, data):
        submit_log_data.delay(LogTypes.activities, json.dumps(data, cls=DecimalEncoder))

    @classmethod
    def submit_process_log(cls, data):
        submit_log_data.delay(LogTypes.process, json.dumps(data, cls=DecimalEncoder))

    @classmethod
    def submit_requests_log(cls, data):
        task_id = submit_log_data.delay(LogTypes.requests, json.dumps(data, cls=DecimalEncoder))
        if settings.DEBUG:
            print("AFEX Logger TID:", task_id)

    @classmethod
    def fetch_error_logs(cls, params):
        return AppLogService().fetch_logs(LogTypes.errors, params)

    @classmethod
    def fetch_activity_logs(cls, params):
        return AppLogService().fetch_logs(LogTypes.activities, params)

    @classmethod
    def fetch_process_logs(cls, params):
        return AppLogService().fetch_logs(LogTypes.process, params)

    @classmethod
    def fetch_request_logs(cls, params):
        return AppLogService().fetch_logs(LogTypes.requests, params)
