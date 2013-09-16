# -*- coding: utf-8 -*-
import web
import logging
logging.basicConfig(level=logging.NOTSET)

dbuser =  'root'
dbpw = 'password'
dbhost = 'localhost'
dbport = 3306
dbname = 'warnings'

try:
    import sae.const
    dbuser = sae.const.MYSQL_USER 
    dbpw = sae.const.MYSQL_PASS 
    dbhost = sae.const.MYSQL_HOST
    dbname = sae.const.MYSQL_DB 
    dbport = int(sae.const.MYSQL_PORT)
except:
    logging.exception('sae const error')


webpydb = web.database(dbn='mysql', user=dbuser, pw=dbpw, host=dbhost, port=dbport, db=dbname)
dbconn = 'mysql://%(dbuser)s:%(dbpw)s@%(dbhost)s:%(dbport)s/%(dbname)s' % locals()
logging.error('dbconn:%s', dbconn)
