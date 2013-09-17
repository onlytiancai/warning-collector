# -*- coding: utf-8 -*-
import web
import os
import datetime

import config
from db import loadsa, unloadsa, User, Warning, WarningCate
import db

web.config._db =db # 让oauth等模块使用model
web.config.debug = True
urls = ["/", 'index',
        "/cates", 'cates',
        "/userinfo", 'userinfo',
        "/send_warning/([^/]+)", 'send_warning',
        "/default", 'default',
        "/logout", 'logout',

        "/qq_login", 'oauth.qqlogin.qqlogin',
        "/qq_callback", 'oauth.qqlogin.qqcallback',
        "/weibo_login", 'oauth.weibologin.weibologin',
        "/weibo_callback", 'oauth.weibologin.weibocallback',
        ]

app = web.application(urls, globals())
wsgiapp = app.wsgifunc()

# 加载sqlalcheym的hook，用于在每个请求前建立dbsession, 请求结束后关闭session
app.add_processor(web.loadhook(loadsa))
app.add_processor(web.unloadhook(unloadsa))

# 为了防止调试时因为auto reload而丢失session
if web.config.get('_session') is None:
    store = web.session.DBStore(config.webpydb, 'sessions')
    session = web.session.Session(app, store)
    web.config._session = session
else:
    session = web.config._session

curdir = os.path.dirname(__file__)
render = web.template.render(os.path.join(curdir, 'templates/'), base='layout',
                             cache=False, globals={'session': session})

def login_required(func):
    def Function(*args,**kargs):
        if 'user' not in session:
            web.seeother('/default',absolute=True)
        else:
            return func(*args,**kargs)
    return Function

class index(object):
    @login_required
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        user_id = session.user.user_id
        cates = web.ctx.db.query(WarningCate).filter_by(user_id=user_id)
        warnings = web.ctx.db.query(Warning).filter_by(user_id=user_id)
        
        data = web.input(cate='all', host=None, appname=None, begin_time=None, end_time=None)
        if data.cate != 'all':
            warnings = warnings.filter_by(cate=data.cate)
        if data.host:
            warnings = warnings.filter_by(host=data.host)
        if data.appname:
            warnings = warnings.filter_by(appname=data.appname)

        today = datetime.datetime.now()
        begin_time = today - datetime.timedelta(days=today.weekday())
        end_time = today + datetime.timedelta(days=(7 - today.weekday() - 1))
        if data.begin_time:
            # 不做异常处理，出错就出错吧，对系统没影响，而且请求是非法的
            begin_time = datetime.datetime.strptime(data.begin_time, '%Y-%m-%d')
        if data.end_time:
            end_time = datetime.datetime.strptime(data.end_time, '%Y-%m-%d')
       
        # 开始时间换算到0点，结束实践换算到12点
        begin_time = datetime.datetime.strptime(begin_time.strftime('%Y-%m-%d ' + '00:00:00'), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time.strftime('%Y-%m-%d ' + '23:59:59'), '%Y-%m-%d %H:%M:%S')

        # 时间范围不能超过7天
        if (end_time - begin_time).total_seconds() > 60 * 60 * 24 * 10:
            raise web.badrequest()
       
        warnings = warnings.filter(Warning.created_on >= begin_time)
        warnings = warnings.filter(Warning.created_on <= end_time)
        
        last_week_begin = begin_time - datetime.timedelta(days=7)
        last_week_end = end_time - datetime.timedelta(days=7)
        next_week_begin = begin_time + datetime.timedelta(days=7)
        next_week_end = end_time + datetime.timedelta(days=7)

        return render.index(web.storage(cates=cates,
                                        warnings=warnings,
                                        begin_time=begin_time.strftime('%Y-%m-%d'),
                                        end_time=end_time.strftime('%Y-%m-%d'),
                                        cate=data.cate,
                                        host=data.host,
                                        appname=data.appname,
                                        last_week_begin=last_week_begin.strftime('%Y-%m-%d'),
                                        last_week_end=last_week_end.strftime('%Y-%m-%d'),
                                        next_week_begin=next_week_begin.strftime('%Y-%m-%d'),
                                        next_week_end=next_week_end.strftime('%Y-%m-%d')
                                        ))


class cates(object):
    def _render(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        result = web.ctx.db.query(WarningCate).filter(WarningCate.user_id == session.user.user_id)
        return render.cates(web.storage(cates=result))

    @login_required
    def GET(self):
        data = web.input(action=None, cate_id=None)
        if data.action == 'del' and data.cate_id:
            cate = web.ctx.db.query(WarningCate).filter_by(user_id=session.user.user_id,
                                                              cate_id=data.cate_id).first()
            if cate:
                web.ctx.db.delete(cate)
                return web.found('/cates')

        return self._render()

    @login_required
    def POST(self):
        data = web.input()
        if not data.cate:
            raise web.badrequest()

        cate = WarningCate(session.user.user_id, data.cate)
        web.ctx.db.add(cate)
        return self._render()


class userinfo(object):
    @login_required
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.userinfo()


class send_warning(object):
    def POST(self, user_id):
        if web.ctx.protocol != 'https':
            raise web.badrequest()
        data = web.input(app_id=None, cate='Default', host="Default",
                         appname="Default", level="0", title=None, content=None)

        # app_id, title, content为必填字段
        if not all([data.app_id, data.title, data.content]):
            raise web.badrequest()

        # user_id和app_id不匹配拒绝请求
        user = web.ctx.db.query(User).filter_by(user_id=int(user_id), app_id=data.app_id).first()
        if not user:
            raise web.forbidden()

        warning = Warning(user_id=int(user_id), title=data.title, content=data.content,
                             level=int(data.level), cate=data.cate, host=data.host, appname=data.appname)
        web.ctx.db.add(warning)


class default(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.default()

class logout(object):
    @login_required
    def GET(self):
        session.kill()
        return web.seeother('/default')

        
if __name__ == "__main__":
    app.run()
