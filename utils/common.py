# coding=utf-8

import functools

from utils.response_code import RET


def require_logined(func):
    @functools.wraps(func)
    def wrapper(request_handler_obj, *args, **kwargs):
        # 根据get_current_user方法进行判断，如果返回的不是一个空字典，则表明用户已经登录
        if request_handler_obj.get_current_user():
            func(request_handler_obj, *args, **kwargs)
        else:
            request_handler_obj.write(
                {"errno": RET.SESSIONERR, "errmsg": '用户未登录'})
    return wrapper
