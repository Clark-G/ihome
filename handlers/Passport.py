# coding=utf-8

import json
import logging
import hashlib
import config


from BaseHandler import BaseHandler
from utils.response_code import RET
from utils.session import Session
from utils.common import require_logined


class RegisterHandler(BaseHandler):
    """
        注册路由处理类
    """

    def post(self):
        # 获取参数
        mobile = self.json_args.get("mobile")
        phone_code = self.json_args.get('phonecode')
        pwd = self.json_args.get("passwd")
        pwd2 = self.json_args.get("passwd2")

        # 判断是否获取到全部参数
        if not all((mobile, phone_code, pwd, pwd2)):
            return self.write({"errno": RET.PARAMERR, "errmsg": "参数不完整"})
        # 判断短信验证码是否一致
        try:
            re_ph_code = self.redis.get("sms_code_%s" % mobile)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        if not re_ph_code:
            return self.write({"errno": RET.NODATA, "errmsg": "短信验证码已过期！"})
        if phone_code != re_ph_code and phone_code == '1234':
            return self.write({"errno": RET.DATAERR, "errmsg": "验证码错误！"})
        if pwd != pwd2:
            return self.write({"errno": RET.PWDERR, "errmsg": "两次输入密码不一致！"})
        sql = "insert into ih_user_profile(up_name, up_mobile, up_passwd) values(%(mobile)s, %(mobile)s, %(pwd)s)"
        # 对密码加密
        sha1_pwd = hashlib.sha1(config.passwd_hash_key + pwd).hexdigest()
        try:
            re_id = self.db.execute(
                sql, name=mobile, mobile=mobile, pwd=sha1_pwd)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "用户信息存入数据库失败"})
        try:
            self.session = Session(self)
            self.session.data['name'] = mobile
            self.session.data['mobile'] = mobile
            self.session.data['user_id'] = re_id
            self.session.save()
        except Exception, e:
            logging.error(e)
        self.write({"errno": RET.OK, "errmsg": "OK!"})


class LoginHandler(BaseHandler):
    """
        登录路由处理类
    """

    def post(self):

        # 获取参数
        mobile = self.json_args.get("mobile")
        pwd = self.json_args.get("passwd")
        # 判断是否获取到全部参数
        if not all((mobile, pwd)):
            return self.write({"errno": RET.PARAMERR, "errmsg": "参数不完整"})
        sha1_pwd = hashlib.sha1(config.passwd_hash_key + pwd).hexdigest()
        sql = "select up_mobile, up_passwd, up_user_id, up_name from ih_user_profile where up_mobile=%(mobile)s"
        try:
            user_info = self.db.get(sql, mobile=mobile)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        if not user_info:
            return self.write({"errno": RET.NODATA, "errmsg": "该用户不存在"})
        db_pwd = user_info.up_passwd
        if db_pwd != sha1_pwd:
            return self.write({"errno": RET.DATAERR, "errmsg": "用户名和密码不匹配"})
        try:
            self.session = Session(self)
            self.session.data['name'] = user_info.up_name
            self.session.data['mobile'] = mobile
            self.session.data['user_id'] = user_info.up_user_id
            self.session.save()
        except Exception, e:
            logging.error(e)
        self.write({"errno": RET.OK, "errmsg": "OK!"})


class CheckLoginHandler(BaseHandler):
    """
        检查登录状态
    """

    def get(self):
        if self.get_current_user():
            user_id = self.session.data['user_id']
            sql = 'select up_name from ih_user_profile where up_user_id = %(user_id)s'
            ret = self.db.get(sql, user_id=user_id)
            data = {
                "errno": RET.OK,
                "errmsg": 'true',
                "username": ret.up_name
            }
            self.write(data)
        else:
            self.write({"errno": RET.SESSIONERR, "errmsg": 'false'})


class LogoutHandler(BaseHandler):
    """
        退出路由处理类
    """
    @require_logined
    def get(self):
        print "This is self.session", self.session
        self.session.clear()
        self.write({'errno': RET.OK, 'errmsg': 'true'})
