# -*- coding: utf-8 -*-
import web
import os

curdir = os.path.dirname(__file__)
render = web.template.render(os.path.join(curdir, 'templates/'), base='layout')

class index(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.index()


class cates(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        return render.cates()


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
