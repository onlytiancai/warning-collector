# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta
import logging

import config
import db

logging.basicConfig(level=logging.NOTSET)

engine = sqlalchemy.create_engine(config.dbconn, echo=False, connect_args={'charset': 'utf8'}, pool_recycle=5)
session = scoped_session(sessionmaker(autoflush=True, bind=engine))


from_user = 'bbbb'


def get_log(from_user, op):
    return session.query(db.LianjianLog).filter_by(from_user=from_user, op=op).first()

def add_log(from_user, op):
    old_log = get_log(from_user, 1)
    if not old_log: # 全新记录
        log = db.LianjianLog(from_user)
        log.op = op 
        log.total_hits = 1
        log.keep_hits = 1
        log.created_on = datetime.now()
        session.add(log)
        logging.debug('add_log new log')
    else: # 有则修改
        logging.debug("exist log:%s", old_log.__dict__)
      
        diff = datetime.now() - old_log.created_on
        # 同一天，直接返回
        if datetime.now().strftime('%Y-%m-%d') == old_log.created_on.strftime('%Y-%m-%d'):
            logging.debug('add_log return')
            return
        elif diff <= timedelta(days=2): # 48小时内连续增加
            old_log.total_hits += 1
            old_log.keep_hits += 1 
            logging.debug('add_log keep_hits += 1')
        else:
            old_log.total_hits += 1
            old_log.keep_hits = 1 
            logging.debug('add_log keep_hits = 1')

    session.commit()

if __name__ == '__main__':
    add_log(from_user, 1)
