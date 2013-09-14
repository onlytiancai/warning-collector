# -*- coding: utf-8 -*-
import web
import os

import db 

curdir = os.path.dirname(__file__)
render = web.template.render(os.path.join(curdir, 'templates/'), base='layout')

user_id = 0

class index(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.index()


class cates(object):
    def _render(self, user_id):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        result = db.session.query(db.WarningCate).filter(db.WarningCate.user_id == user_id)
        return render.cates(dict(cates=result))

    def GET(self):
        data = web.input(action=None, cate_id=None)
        if data.action == 'del' and data.cate_id:
            cate = db.session.query(db.WarningCate).filter_by(user_id=user_id,cate_id=data.cate_id).first()
            if cate:
                db.session.delete(cate)
                db.session.commit()
                return web.found('/cates')

        return self._render(user_id)

    def POST(self):
        data = web.input()
        if not data.cate:
            raise web.badrequest() 

        cate = db.WarningCate(user_id, data.cate)
        print 1111, data.cate
        db.session.add(cate)
        db.session.commit()
        return self._render(user_id)


class userinfo(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.userinfo()


class about(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.about()

urls = ["/", index,
        "/cates", cates,
        "/userinfo", userinfo,
        "/about", about,
        ]

app = web.application(urls, globals())
wsgiapp = app.wsgifunc()

if __name__ == "__main__":
    app.run()
