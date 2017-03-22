from tornado.web import url, StaticFileHandler
from handlers import Passport, VerifyCode, Profile, House
import os

html_path = {
    "path": os.path.join(os.path.dirname(__file__), "html"),
    "default_filename": "index.html"
}


handlers = [
    url(r'^/api/imagecode', VerifyCode.ImageCodeHanlder, name='imagecode'),
    url(r'^/api/smscode', VerifyCode.SMSCodeHandler, name='smscode'),
    url(r'^/api/register', Passport.RegisterHandler, name='register'),
    url(r'^/api/login', Passport.LoginHandler, name='login'),
    url(r'^/api/check_login', Passport.CheckLoginHandler, name='check_login'),
    url(r'/api/logout', Passport.LogoutHandler, name='logout'),
    url(r'/api/profile', Profile.ProfileHanlder, name='profile'),
    url(r'/api/profile/avatar', Profile.AvatarHandler, name='avatar'),
    url(r'/api/profile/name', Profile.UserNameHandler, name='username'),
    url(r'/api/profile/auth', Profile.AuthenticateHandler, name='auth'),
    url(r'^/api/house/index', House.IndexHandler, name='index'),
    url(r'^/api/house/list', House.HouseListHandler, name='list'),
    url(r'/api/house/myhouse', House.MyHouseHandler, name='myhouse'),
    url(r'/api/house/area', House.AreaInfoHandler, name='area'),
    url(r'/api/house/newhouse', House.NewHouseHandler, name='newhouse'),
    url(r'/api/house/image', House.HouseImageHandler, name='image'),
    url(r'^/(.*)', StaticFileHandler, html_path),


]
