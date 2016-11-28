# coding=utf-8

import os


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    # "template_path":os.path.join(os.path.dirname(__file__), 'template'),
    "debug": True,
    'xsrf_cookies': True,
    "cookie_secret": '97UvXVCKSgu8/H4MgL9YZgVnIulgjEMmhcKHS9SwPqo='
}
db_settings = {
    "host": "127.0.0.1",
    "database": "ihome",
    "user": "root",
    "password": "mysql"
}
redis_settings = {
    "host": "127.0.0.1",
    "port": "6379"
}

log_file = os.path.join(os.path.dirname(__file__), 'logs/log')
log_level = "debug"

# session有效时间
session_expires = 86400


passwd_hash_key = "ihome@$^*"  # 密码加密salt

image_url_prefix = "http://oh71s68xs.bkt.clouddn.com/"  # 七牛图片的域名
