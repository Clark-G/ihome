# coding=utf-8


import json
import math
import constants
import logging

from BaseHandler import BaseHandler
from config import image_url_prefix
from utils.response_code import RET
from utils.common import require_logined
from utils.image_storage import store_image


class IndexHandler(BaseHandler):
    """
        主页信息
    """
    def get(self):
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_houses = ret
        else:
            try:
                sql = """
                    select distinct a.hi_house_id,a.hi_title,a.hi_order_count,a.hi_index_image_url 
                    from ih_house_info a inner join ih_house_image b on a.hi_house_id=b.hi_house_id 
                    order by a.hi_order_count desc limit %s;
                """
                house_ret = self.db.query(sql % constants.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write({"errno":RET.DBERR, "errmsg":"get data error"})
            if not house_ret:
                return self.write({"errno":RET.NODATA, "errmsg":"no data"})
            houses = []
            for l in house_ret:
                if not l["hi_index_image_url"]:
                    continue
                # print "This is img_url", l["hi_index_image_url"]
                house = {
                    "house_id":l["hi_house_id"],
                    "title":l["hi_title"],
                    "img_url": image_url_prefix + l["hi_index_image_url"]
                }
                houses.append(house)
            json_houses = json.dumps(houses)
            try:
                self.redis.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json_houses)
            except Exception as e:
                logging.error(e)
        data = '{"errno":"0", "errmsg":"OK", "houses":%s}' % json_houses
        self.write(data)        




class MyHouseHandler(BaseHandler):
    """
        我的房源信息展示
    """
    @require_logined
    def get(self):
        user_id = self.session.data['user_id']

        try:
            sql = """select a.hi_house_id, a.hi_title, a.hi_price, a.hi_ctime, b.ai_name, a.hi_index_image_url
                from ih_house_info a left join ih_area_info b on a.hi_area_id = b.ai_area_id where a.hi_user_id=%s            
            """
            ret = self.db.query(sql, user_id)
            # print "This is house_info", ret
        except Exception, e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "查询失败"})
        houses = []
        if ret:
            for house_info in ret:
                house = {
                    "house_id": house_info["hi_house_id"],
                    "title": house_info["hi_title"],
                    "price": house_info["hi_price"],
                    "ctime": house_info["hi_ctime"].strftime("%Y-%m-%d"),
                    "area_name": house_info["ai_name"],
                    "img_url": image_url_prefix + house_info["hi_index_image_url"] if house_info["hi_index_image_url"] else ""
                }
                # print "This is house infomation", house
                houses.append(house)
        self.write({"errno": RET.OK, "errmsg": "OK", "houses": houses})


class AreaInfoHandler(BaseHandler):
    """
        获取区域信息
    """

    def get(self):
        # 先从Redis中获取数据
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.debug(ret)
            logging.info("hit redis cache")
            # data = {
            #     "errno": RET.OK,
            #     "errmsg": "OK",
            #     "areas": ret
            # }
            return self.write('{"errno":%s, "errmsg":"OK", "areas":%s}' % (RET.OK, ret))
        # 未从Redis中拿到数据，去数据库查询
        try:
            ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "get data error"})
        if not ret:
            return self.write({"errno": RET.NODATA, "errmsg": "no area data"})
        areas = []
        for l in ret:
            area = {
                "area_id": l["ai_area_id"],
                "name": l["ai_name"]
            }
            areas.append(area)
        # 将数据缓存到Redis中
        try:
            self.redis.setex(
                "area_info", constants.AREA_INFO_REDIS_EXPIRES_SECONDS, json.dumps(areas))
        except Exception as e:
            logging.error(e)
        # 返回客户端
        data = {
            "errno": RET.OK,
            "errmsg": "OK",
            "areas": areas
        }        
        self.write(data)


class NewHouseHandler(BaseHandler):
    '''
        发布新房源
    '''
    @require_logined
    def post(self):

        # 获取所需参数并判断是否完整
        user_id = self.session.data['user_id']
        # user_id = self.json_args.get('user_id')
        title = self.json_args.get('title')
        price = self.json_args.get('price')
        dis = self.json_args.get('area_id')
        addr = self.json_args.get('address')
        room_count = self.json_args.get('room_count')
        acreage = self.json_args.get('acreage')
        house_unit = self.json_args.get('unit')
        house_capacity = self.json_args.get('capacity')
        beds = self.json_args.get('beds')
        deposit = self.json_args.get('deposit')
        min_days = self.json_args.get('min_days')
        max_days = self.json_args.get('max_days')
        facility = self.json_args.get('facility')
        p_list = [user_id, title, price, dis, addr, room_count, acreage, house_unit, house_capacity,
                  beds, deposit, min_days, max_days, facility]
        print "this is p_list", p_list
        if not all(p_list):
            return self.write({'errno': RET.PARAMERR, 'errmsg': '参数不完整'})
        try:
            price = int(price)*100
            deposit = int(deposit)*100
        except Exception as e:
            return self.write(dict(errno=RET.PARAMERR, errmsg="参数错误"))

        # 插入房屋基本信息
        try:
            sql = """insert into ih_house_info(hi_user_id, hi_title, hi_price, hi_area_id, hi_address, 
                        hi_room_count, hi_acreage, hi_house_unit, hi_capacity, hi_beds, hi_deposit, 
                        hi_min_days, hi_max_days) values(%(user_id)s, %(title)s, %(price)s, %(dis)s, 
                        %(addr)s, %(room_count)s, %(acreage)s, %(house_unit)s, %(house_capacity)s, %(beds)s,
                        %(deposit)s, %(min_days)s, %(max_days)s)"""
            data = {
                'user_id': user_id,
                'title': title,
                'price': price,
                'dis': dis,
                'addr': addr,
                'room_count': room_count,
                'acreage': acreage,
                'house_unit': house_unit,
                'house_capacity': house_capacity,
                'beds': beds,
                'deposit': deposit,
                'min_days': min_days,
                'max_days': max_days

            }
            house_id = self.db.execute(sql, **data)

        except Exception, e:
            logging.error(e)
            return self.write({'errno': RET.DBERR, 'errmsg': '插入房屋基本信息失败'})

        # 插入房屋配套设施信息
        try:
            for f in facility:
                f_sql = "insert into ih_house_facility(hf_house_id, hf_facility_id) values(%(house_id)s, %(facility_id)s)"
                f_ret = self.db.execute(
                    f_sql, house_id=house_id, facility_id=f)
        except Exception, e:
            logging.error(e)
            try:
                self.db.execute(
                    'delete from ih_house_info where hi_house_id = %(house_id)s', house_id=house_id)
            except Exception, e:
                logging.error(e)
                return self.write({'errno': RET.DBERR, 'errmsg': '删除房屋基本失败'})
            else:
                return self.write({'errno': RET.DBERR, 'errmsg': '插入房屋配套设施信息失败'})
        self.redis.delete('home_page_data')
        self.write({'errno': RET.OK, 'errmsg': 'OK', 'house_id': house_id})


class HouseImageHandler(BaseHandler):
    """
        上传房屋照片
    """
    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        house_id = self.get_argument("house_id")
        house_image = self.request.files["house_image"][0]["body"]
        img_name = store_image(house_image)
        if not img_name:
            return self.write({"errno": RET.THIRDERR, "errmsg": "qiniu error"})
        try:
            sql = """insert into ih_house_image(hi_house_id,hi_url) values(%s,%s);
                    update ih_house_info set hi_index_image_url=%s where hi_house_id=%s 
                    and hi_index_image_url is null"""
            self.db.execute(sql, house_id, img_name, img_name, house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "upload failed"})
        img_url = image_url_prefix + img_name
        self.write({"errno": RET.OK, "errmsg": "OK", "url": img_url})


class HouseListHandler(BaseHandler):
    """
        房屋列表信息
    """

    def get(self):
        area_id = self.get_argument("aid", "")
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        try:
            redis_key = "hs_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)
            ret = self.redis.hget(redis_key, page)
        except Exception as e:
            logging.error(e)
        if ret:
            logging.info("hit redis")
            return self.write(ret)

        page = int(page)

        sql_where_li = []
        sql_params = {}

        if area_id:
            sql_where_li.append("hi_area_id=%(area_id)s")
            sql_params["area_id"] = int(area_id)

        if start_date and end_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or not (oi_begin_date<=%(end_date)s and oi_end_date>=%(start_date)s))")
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or oi_end_date<%(start_date)s)")
            sql_params["start_date"] = start_date
        elif end_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or oi_begin_date<%(end_date)s)")
            sql_params["end_date"] = end_date

        sql_where = " and ".join(sql_where_li)
        if "" != sql_where:
            sql_where = " where " + sql_where

        try:
            logging.debug("select count(distinct hi_house_id) counts from ih_house_info left join ih_order_info on hi_house_id=oi_house_id" + sql_where)
            ret = self.db.get("select count(distinct hi_house_id) counts from ih_house_info left join ih_order_info on hi_house_id=oi_house_id" + sql_where, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.DBERR, "errmsg":"get total_page error"})
        if 0 == ret["counts"]:
            return self.write({"errno":RET.OK, "errmsg":"OK", "total_page":0, "data":[]})
        total_page = int(math.ceil(float(ret["counts"]) / constants.HOUSE_LIST_PAGE_CAPACITY))
        if page > total_page:
            return self.write({"errno":RET.OK, "errmsg":"OK", "total_page":total_page, "data":[]})

        sql = """select distinct hi_house_id,hi_title,hi_price,hi_room_count,hi_order_count,hi_index_image_url,
                    hi_address,up_avatar,hi_order_count,hi_price,hi_ctime from ih_house_info left join ih_order_info 
                    on hi_house_id=oi_house_id inner join ih_user_profile on hi_user_id=up_user_id"""
        sql += sql_where
        sql += " order by "
        if "booking" == sort_key:
            sql += "hi_order_count desc"
        elif "price-inc" == sort_key:
            sql += "hi_price asc"
        elif "price-des" == sort_key:
            sql += "hi_price desc"
        else:
            sql += "hi_ctime desc"
        if 1 == page:
            sql += " limit %s" % (constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REIDS_CACHED_PAGE)
        else:
            sql += " limit %s,%s" % ((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REIDS_CACHED_PAGE)
        try:
            logging.debug(sql)
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.DBERR, "errmsg":"get data error"})
        if not ret:
            return self.write({"errno":RET.OK, "errmsg":"OK", "total_page":total_page, "data":[]})
        houses = []
        for l in ret:
            house = {
                "house_id":l["hi_house_id"],
                "title":l["hi_title"],
                "price":l["hi_price"],
                "room_count":l["hi_room_count"],
                "order_count":l["hi_order_count"],
                "address":l["hi_address"],
                "img_url":image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                "avatar_url":image_url_prefix + l["up_avatar"] if l["up_avatar"] else ""
            }
            houses.append(house)
        logging.debug(houses)
        page_data = houses[0:constants.HOUSE_LIST_PAGE_CAPACITY]
        self.write({"errno":RET.OK, "errmsg":"OK", "total_page":total_page, "data":page_data})
        redis_data = {
            str(page):json.dumps({"errno":RET.OK, "errmsg":"OK", "total_page":total_page, "data":page_data})
        }
        i = 1
        while 1:
            page_data = houses[(i*constants.HOUSE_LIST_PAGE_CAPACITY):((i+1)*constants.HOUSE_LIST_PAGE_CAPACITY)]
            if not page_data:
                break
            redis_data[str(page+i)] = json.dumps({"errno":RET.OK, "errmsg":"OK", "total_page":total_page, "data":page_data})  
            i += 1

        redis_key = "hs_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)
        try:
            self.redis.hmset(redis_key, redis_data)
        except Exception as e:
            logging.error(e)
            return
        try:
            self.redis.expire(redis_key, constants.HOUSE_LIST_REDIS_EXPIRE_SECOND)
        except Exception as e:
            logging.error(e)
            self.redis.delete(redis_key)