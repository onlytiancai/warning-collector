# -*- coding: utf-8 -*-
import web
import uuid
import urlparse
import json
import logging

from . import config
from .oauth import OAuth

qqOAuth = OAuth(
    name='qq',
    client_id=config.qq_app_id,
    client_secret=config.qq_app_key,
    base_url='https://graph.qq.com',
    access_token_url='https://graph.qq.com/oauth2.0/token',
    authorize_url='https://graph.qq.com/oauth2.0/authorize')


class qqlogin(object):
    def GET(self):
        state = uuid.uuid1()
        web.setcookie('qqstate', state)
        url = qqOAuth.get_authorize_url(response_type='code',
                                        redirect_uri=config.qq_callback,
                                        state=state)
        return web.redirect(url)


class qqcallback(object):
    def get_access_token(self, code):
        result = qqOAuth.get_access_token('GET',
                                          code=code,
                                          grant_type='authorization_code',
                                          redirect_uri=config.qq_callback)
        result = dict(urlparse.parse_qsl(result))
        if 'access_token' not in result:
            raise web.badrequest()
        return result['access_token']

    def get_openid(self, access_token):
        result = qqOAuth.request('GET', '/oauth2.0/me', access_token=access_token)
        result = result.lstrip("callback( ")
        result = result.rstrip(" );\n")
        result = json.loads(result)
        if 'openid' not in result:
            raise web.forbidden()
        return result['openid']

    def get_nickname(self, access_token, openid):
        result = qqOAuth.request('GET', '/user/get_user_info',
                                 access_token=access_token,
                                 openid=openid,
                                 oauth_consumer_key=config.qq_app_id)
        result = json.loads(result)
        return result['nickname']

    def GET(self):
        import uuid
        import datetime
        db = web.config._db
        session = web.config._session

        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        code = web.input().code
        state = web.input().state
        cookie_state = web.cookies().get('qqstate')
        if state != cookie_state:
            raise web.Forbidden()

        if code:
            access_token = self.get_access_token(code)
            openid = self.get_openid(access_token)
            nickname = self.get_nickname(access_token, openid)

            oauth_user_id = 'qq:' + openid
            user = web.ctx.db.query(db.User).filter_by(oauth_user_id=oauth_user_id).first()
            if not user:
                user = db.User(openid)
                user.app_id = str(uuid.uuid1())
                user.user_name = nickname
                user.oauth_user_id = oauth_user_id
                user.created_on = datetime.datetime.now()
                web.ctx.db.add(user)
                web.ctx.db.commit()

            session.user = web.storage(app_id=user.app_id, user_id=user.user_id, user_name=user.user_name) 
            logging.info('qq logined:%s', session.user)
            
            return web.found('/')
