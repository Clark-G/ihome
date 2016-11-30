import json
from tornado.web import RequestHandler, StaticFileHandler
from utils.session import Session

class BaseHandler(RequestHandler):
    """
        The base class of handlers
    """

    # def __init__(self, *args, **kwargs):
    #     super(RequestHandler, self).__init__(*args, **kwargs)
    #     self.session = Session(self)

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def initialize(self):
        pass

    def prepare(self):
        self.xsrf_token
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            # print 'this is body', self.request.body
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def write_error(self, status_code, **kwargs):
        pass

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def on_finish(self):
        pass

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data

class StaticFileHandler(StaticFileHandler):
    """
        redefine the class to set xsrf_token
    """

    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
