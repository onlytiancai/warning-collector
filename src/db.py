# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from sqlalchemy.exc import DisconnectionError
import web

import config

engine = sqlalchemy.create_engine(config.dbconn, echo=False, connect_args={'charset': 'utf8'}, pool_recycle=5)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# 防止mysql gone away，从池里取连接前先测试连接是否已断开。
def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


sqlalchemy.event.listen(engine, 'checkout', checkout_listener)


class WebSession(Base):
    __tablename__ = 'sessions'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    session_id = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, unique=True, primary_key=True)
    atime = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=False, default=sqlalchemy.func.current_timestamp)
    data = sqlalchemy.Column(sqlalchemy.TEXT)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    app_id = sqlalchemy.Column(sqlalchemy.String(128))
    oauth_user_id = sqlalchemy.Column(sqlalchemy.String(128), index=True)
    user_name = sqlalchemy.Column(sqlalchemy.String(128))
    extend = sqlalchemy.Column(sqlalchemy.TEXT)
    created_on = sqlalchemy.Column(sqlalchemy.DateTime)

    def __init__(self, oauth_user_id):
        self.oauth_user_id = oauth_user_id


class Warning(Base):
    __tablename__ = 'warnings'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    warning_id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    cate = sqlalchemy.Column(sqlalchemy.String(32))
    host = sqlalchemy.Column(sqlalchemy.String(32))
    appname = sqlalchemy.Column(sqlalchemy.String(32))
    level = sqlalchemy.Column(sqlalchemy.SmallInteger)
    title = sqlalchemy.Column(sqlalchemy.String(256))
    content = sqlalchemy.Column(sqlalchemy.String(8000))
    created_on = sqlalchemy.Column(sqlalchemy.DateTime, index=True)

    def __init__(self, user_id, title, content, level=0,
                 cate="Default", host="Default", appname="Default"):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.level = level
        self.cate = cate
        self.host = host
        self.appname = appname
        self.created_on = datetime.now()


class WarningCate(Base):
    __tablename__ = 'warning_cates'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    cate_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    cate = sqlalchemy.Column(sqlalchemy.String(32))

    def __init__(self, user_id, cate):
        self.user_id = user_id
        self.cate = cate


class LianjianLog(Base):
    __tablename__ = 'lianjian_log'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    log_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    from_user = sqlalchemy.Column(sqlalchemy.String(64), index=True)
    op = sqlalchemy.Column(sqlalchemy.SmallInteger)
    total_hits = sqlalchemy.Column(sqlalchemy.Integer)
    keep_hits = sqlalchemy.Column(sqlalchemy.Integer)
    created_on = sqlalchemy.Column(sqlalchemy.DateTime)

    def __init__(self, from_user):
        self.from_user = from_user 


Base.metadata.create_all(engine)


def loadsa():
    session = scoped_session(sessionmaker(autoflush=True, bind=engine))
    web.ctx.sadbsession = session
    web.ctx.db = session()
    

def unloadsa():
    web.ctx.db.close()
    web.ctx.sadbsession.remove()
