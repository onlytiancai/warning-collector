# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import config

engine = sqlalchemy.create_engine(config.dbconn, echo=True, connect_args={'charset': 'utf8'}, poolclass=NullPool)
Base = declarative_base()
Session = sessionmaker(bind=engine)

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
