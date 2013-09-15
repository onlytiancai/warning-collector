# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime

import config

engine = sqlalchemy.create_engine(config.dbconn, echo=True, connect_args={'charset': 'utf8'}, poolclass=NullPool)
Base = declarative_base()
Session = sessionmaker(bind=engine)

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
    sina_user_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    user_name = sqlalchemy.Column(sqlalchemy.String(128))
    created_on = sqlalchemy.Column(sqlalchemy.DateTime)

class Warning(Base):
    __tablename__ = 'warnings'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __mapper_args__ = {'always_refresh': True}

    warning_id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    cate = sqlalchemy.Column(sqlalchemy.String(32))
    host = sqlalchemy.Column(sqlalchemy.String(32))
    appname= sqlalchemy.Column(sqlalchemy.String(32))
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

Base.metadata.create_all(engine) 
session = Session()
