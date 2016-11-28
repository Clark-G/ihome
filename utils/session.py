# coding=utf-8

import uuid
import logging
import json
import config


class Session(object):
    """
            生成session的类
    """

    def __init__(self, request_handler):
        self.request_handler = request_handler
        self.session_id = self.request_handler.get_secure_cookie('session_id')
        # print "这是从cookie中获取的",self.session_id
        if not self.session_id:
            # 用户第一次访问，生成一个session_id
            self.session_id = uuid.uuid4().get_hex()
            self.data = {}
            # print "这是第一次生成的",self.session_id
        else:
            # 通过session_id去redis中获取对应的数据
            try:
                data = self.request_handler.redis.get("sess_%s" % self.session_id)
                # print "这是从redis取出的session_id对应的数据",data
            except Exception, e:
                logging.error(e)
                self.data = {}
            if not data:
                self.data = {}
            else:
                self.data = json.loads(data)

    def save(self):
        json_data = json.dumps(self.data)
        try:
            self.request_handler.redis.setex("sess_%s" % self.session_id,
                             config.session_expires, json_data)
        except Exception, e:
            logging.error(e)
            raise Exception("save session failed")
        else:
            self.request_handler.set_secure_cookie(
                "session_id", self.session_id)

    def clear(self):
        self.request_handler.clear_cookie("session_id")
        try:
            self.request_handler.redis.delete("sess_%s" % session_id)
        except Exception, e:
            logging.error(e)
