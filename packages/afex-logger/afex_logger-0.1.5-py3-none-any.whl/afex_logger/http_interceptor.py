import json
import traceback

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from afex_logger.util import LogUtil

successful_status = {200, 201, 302, 301}


class LogMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.request_time = timezone.now()

    def __call__(self, request, *args, **kwargs):
        self.process_request(request)
        response = self.process_response(request)
        return response

    def process_request(self, request):
        return None

    def process_response(self, request):
        data = None
        try:
            raw_body = request.body
            raw_body = raw_body.decode("utf-8")
            if raw_body:
                data = json.loads(raw_body)
        except:
            pass

        response = self.get_response(request)

        has_exception = not isinstance(response, HttpResponse)

        path = request.path_info

        excluded_path_patterns = getattr(settings, 'LOG_EXCLUDED_PATH_PATTERNS', [])
        excluded_path_patterns += ['media/',"static/"]

        for p in excluded_path_patterns:
            if p in path:
                return response

        response_time = timezone.now()

        if request.method in ('HEAD', 'OPTIONS', 'TRACE'):
            return response

        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        else:
            user = None

        rest_content_types = getattr(settings, 'LOG_REST_CONTENT_TYPES', [])
        req_content_type = request.META.get('CONTENT_TYPE', '')

        response_type = 'http'

        if "/api/" in path or req_content_type in rest_content_types:
            response_type = 'rest'

        if response_type == 'http':
            response_body = 'http content'
        else:
            if response.streaming:
                response_body = "Streamed Content"
            else:
                response_body = response.content.decode('utf-8')

        if not data:
            data = {}

        # password, csrf token are intentionally removed from list
        keys = getattr(settings, 'LOG_DATA_EXCLUSION_KEYS', []) + ['password', 'csrfmiddlewaretoken']

        for key in keys:
            if key in data:
                _ = data.pop(key)

        log_data = {
            "date": timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'host_name': request.META.get('REMOTE_HOST', ''),
            'user': {"id": user.id, "username": user.username} if user else None,
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'http_method': request.method,
            'http_referer': request.META.get('HTTP_REFERER', ''),
            'path_info': path,
            'post_data': data,
            'response_status_code': response.status_code,
            'response_type': response_type,
            'response_reason_phrase': response.reason_phrase,
            'response_body': response_body if not has_exception else None,
            'attempt_time': self.request_time,
            'response_time': response_time
        }

        LogUtil.submit_requests_log(log_data)
        return response

    def process_exception(self, request, exception):
        self.exception = str(exception)
        self.traceback = traceback.format_exc()
