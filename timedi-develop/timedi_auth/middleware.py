import threading

from django.utils.deprecation import MiddlewareMixin

request_cfg = threading.local()


class RouterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        words = request.META.get("HTTP_REFERER")
        if words and words.startswith("http://180.149.241.208"):
            request_cfg.cfg = "staging"
            return None

    def process_response(self, request, response):
        if hasattr(request_cfg, 'cfg'):
            del request_cfg.cfg
        return response


class DatabaseRouter(object):
    def _default_db(self):
        if hasattr(request_cfg, 'cfg'):
            return request_cfg.cfg
        else:
            return 'default'

    def db_for_read(self, model, **hints):
        return self._default_db()

    def db_for_write(self, model, **hints):
        return self._default_db()
