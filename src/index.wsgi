# -*- coding: utf-8 -*-
import sae
from warning_web import wsgiapp
application = sae.create_wsgi_app(wsgiapp)
