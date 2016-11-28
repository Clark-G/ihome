# coding=utf-8

import logging
import constants
import random
import re

from BaseHandler import BaseHandler
from utils.captcha.captcha import captcha
from utils.response_code import RET
from libs.yuntongxun.CCP import ccp


class ImageCodeHanlder(BaseHandler):
    """
        图片验证码处理类
    """

    def get(self):
        code_id = self.get_argument("codeid")
        pre_code_id = self.get_argument("precodeid")
        if pre_code_id:
            try:
                self.redis.delete("image_code_%s" % pre_code_id)
            except Exception, e:
                logging.error(e)
        # name 图片验证码名称
        # text 图片验证码文本
        # image 图片验证码二进制数据
        name, text, image = captcha.generate_captcha()
        # print "This is",text
        # print "This is",code_id
        try:
            self.redis.setex("image_code_%s" % code_id,
                             constants.IMAGE_CODE_EXPIRES_SECONDS, text)
            image_code_id = "image_code_" + code_id
            # print "插入前", image_code_id
            # print "This is", self.redis.get(image_code_id)
            # print "插入成功"
        except Exception, e:
            logging.error(e)
            self.write("")
        else:
            self.set_header("Content-Type", "image/jpg")
            self.write(image)


class SMSCodeHandler(BaseHandler):
    """docstring for SMSCodeHandler"""

    def post(self):
        # 获取参数
        mobile = self.json_args.get("mobile")
        image_code_id = self.json_args.get("image_code_id")
        image_code_text = self.json_args.get("image_code_text")
        if not all((mobile, image_code_id, image_code_text)):
            return self.write({"errno": RET.PARAMERR, "errmsg": "参数不完整"})
        if not re.match(r'1\d{10}', mobile):
            return self.write({"errno": RET.PARAMERR, "errmsg": "手机号错误"})
        # 判断图片验证码
        try:
            real_image_code_text = self.redis.get(
                "image_code_%s" % image_code_id)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        if not real_image_code_text:
            return self.write({"errno": RET.NODATA, "errmsg": "验证码已过期！"})
        if real_image_code_text.lower() != image_code_text.lower():

            return self.write({"errno": RET.DATAERR, "errmsg": "验证码错误！"})
        try:
            ret = self.db.get('select up_mobile from ih_user_profile where up_mobile =%s' % mobile)
        except Exception, e:
            logging.error(e)
            # return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        else:
            if ret:
                return self.write({"errno": RET.DATAEXIST, "errmsg": "该手机号已被注册！"})

         # 如果图片验证码匹配成功，生成一个随机验证码
        sms_code = "%04d" % random.randint(0, 9999)
        try:
            self.redis.setex("sms_code_%s" % mobile,
                             constants.SMS_CODE_EXPIRES_SECONDS, sms_code)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "生成短信验证码错误！"})

        # 发送短信
        try:
            ccp.sendTemplateSMS(
                mobile, [sms_code, constants.SMS_CODE_EXPIRES_SECONDS / 60], 1)
        except Exception, e:
            return self.write({"errno": RET.THIRDERR, "errmsg": "发送失败！"})

        self.write({"errno": RET.OK, "errmsg": "OK!"})
