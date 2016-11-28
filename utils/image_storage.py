# coding=utf-8

import qiniu.config
import logging

from qiniu import Auth, put_data, etag, urlsafe_base64_encode

# 设置Access Key 和 Secret Key
access_key = 'pges5ZpuQD7VhA-0W50myuMaT_DllWlsFV85Cob6'
secret_key = 'WKjj2QQA67MwyEe_sF1cAvbwyRgbBBrmNnLsIBz5'

# 要上传的空间
bucket_name = 'ihome'


def store_image(data):
    """
        七牛云存储上传文件接口
    """
    if not data:
        return None

    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        ret, info = put_data(token, None, data)
        print 'ret is %s and info is %s ' %(ret, info)
    except Exception, e:
        logging.error(e)
        raise Exception("上传文件到七牛错误")
    if info and info.status_code != 200:
    	raise Exception('上传文件到七牛错误')
    return ret['key']


if __name__ == '__main__':
	file_name = raw_input('输入上传的文件')
	file = open(file_name, 'rb')
	data = file.read()
	key = store_image(data)
	print key
	file.close()