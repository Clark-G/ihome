# coding=utf-8

import logging
import config

from BaseHandler import BaseHandler
from utils.common import require_logined
from utils.response_code import RET
from utils.image_storage import store_image


class ProfileHanlder(BaseHandler):
    """
        用户中心个人信息处理类
    """
    @require_logined
    def get(self):
        user_id = self.session.data['user_id']
        sql = 'select up_avatar, up_name, up_mobile from ih_user_profile where up_user_id=%(user_id)s'
        try:
            db_re = self.db.get(sql, user_id=user_id)
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        if not db_re.up_avatar:
            image_url = ''
        else:
            image_url = config.image_url_prefix + db_re.up_avatar
        data = {
            "errno": RET.OK,
            "errmsg": "true",
            'username': db_re.up_name,
            'mobile': self.session.data['mobile'],
            'avatar': image_url
        }
        self.write(data)


class AvatarHandler(BaseHandler):
    """
        上传头像路由处理类
    """

    @require_logined
    def post(self):
        # print "This is request headers", self.request.headers
        user_id = self.session.data['user_id']
        try:
            avatar = self.request.files['avatar'][0]['body']
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        try:
            img_name = store_image(avatar)
        except Exception, e:
            logging.error(e)
            img_name = None
        if not img_name:
            return self.write({'errno': RET.THIRDERR, 'errmsg': 'qiniu error'})
        try:
            sql = 'update ih_user_profile set up_avatar = %(img_name)s where up_user_id=%(user_id)s'
            ret = self.db.execute(sql, img_name=img_name, user_id=user_id)
        except Exception, e:
            logging.error(e)
            return self.write({'errno': RET.DBERR, 'errmsg': 'upload failed'})
        img_url = config.image_url_prefix + img_name
        data = {
            "errno": RET.OK,
            "errmsg": "OK",
            'url': img_url
        }
        self.write(data)


class UserNameHandler(BaseHandler):
    """
            用户名修改
    """

    @require_logined
    def post(self):
        user_id = self.session.data['user_id']
        uname = self.json_args.get('name')
        if not uname:
            return self.write({"errno": RET.PARAMERR, "errmsg": "请输入要更改的用户名"})
        try:
            sql = 'select up_name from ih_user_profile where up_name=%s'
            ret = self.db.get(sql, uname)
        except Exception, e:
            logging.error(e)

        if ret:
            return self.write({'errno': RET.DATAEXIST, 'errmsg': '该用户名已存在，请重新设置'})

        try:
            sql = 'update ih_user_profile set up_name = %(name)s where up_user_id =%(user_id)s'
            self.db.execute(sql, name=uname, user_id=user_id)
        except Exception, e:
            logging.error(e)
            return self.write({'errno': RET.DBERR, 'errmsg': '修改数据信息失败'})
        data = {
            "errno": RET.OK,
            "errmsg": "OK",
            'uername': uname
        }
        self.write(data)


class AuthenticateHandler(BaseHandler):
    """
        用户实名信息认证
    """
    @require_logined
    def get(self):
        user_id = self.session.data['user_id']
        if not user_id:
            return self.write({'errno': RET.SESSIONERR, 'errmsg': '用户未登录'})
        # print "This is user_id", user_id
        try:
            sql = 'select up_real_name, up_id_card from ih_user_profile where up_user_id = %s'
            ret = self.db.get(sql, user_id)
            # print '这是实名认证信息', ret
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询出错"})
        if not ret:
            return self.write({'errno': RET.NODATA, 'errmsg': '用户未认证'})
        data = {
            'errno': RET.OK,
            'errmsg': 'true',
            'real_name': ret.up_real_name,
            'id_card': ret.up_id_card
        }
        self.write(data)

    @require_logined
    def post(self):
        user_id = self.session.data['user_id']
        real_name = self.json_args.get('real_name')
        id_card = self.json_args.get('id_card')
        if not all([real_name, id_card]):
            return self.write({'errno': RET.PARAMERR, 'errmsg': '参数不完整'})
        sql = 'update ih_user_profile set up_real_name = %(real_name)s, up_id_card = %(id_card)s where up_user_id=%(user_id)s'
        try:
            self.db.execute(sql, real_name=real_name,
                            id_card=id_card, user_id=user_id)
        except Exception, e:
            logging.error(e)
            return self.write({'errno': RET.DBERR, 'errmsg': '插入认证信息失败'})
        data = {
            'errno': RET.OK,
            'errmsg': 'true',
            'real_name': real_name,
            'id_card': id_card
        }
        self.write(data)
