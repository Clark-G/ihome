# coding=utf-8

from tornado.web import Application, RequestHandler, url
from tornado.ioloop import IOLoop
from tornado.options import options, define, parse_command_line
from tornado.httpserver import HTTPServer
from urls import handlers
from config import *
import redis
import json
import torndb
import time

# define a argument parse from command line
define("port", default=8000, type=int)


class Application(Application):
    """
        Redefine the Application class to add db connection with mysql database
    """

    def __init__(self, *args, **kwargs):

        # call the __init__ parent class method
        super(Application, self).__init__(handlers, **settings)

        # add the db attribute of application
        self.db = torndb.Connection(**db_settings)

        # add the redis attribute of application
        self.redis = redis.StrictRedis(**redis_settings)
        # print self.redis


def main():
    # options.logging = log_level
    # options.log_file_prefix = log_file
    parse_command_line()
    app = Application()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
