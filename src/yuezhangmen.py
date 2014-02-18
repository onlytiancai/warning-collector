# -*- coding: utf-8 -*-
import web
import hashlib
from xml.etree import ElementTree
import logging
from datetime import datetime, timedelta

from db import LianjianLog

TOKEN = '855dde440a874ef798227147f6686f55'

welcom_txt = u'''改变世界，从改变自己开始，从现在开始每天"练剑"吧，总共5招。

(#1): 每天睡个好觉
(#2): 每天保持好心情
(#3): 每天学习半小时
(#4): 每天运动半小时
(#5): 每天陪陪家人

回复括号内的文字记录今日的练习成果。

如果你感觉武功已经很高了，可以回复"##"来和别人比武。

'''
sleep_reply_txt = u'恭喜你，睡了个好觉，精力充沛才能做好事情。'
happy_reply_txt = u'无论什么时候，都要保持好心情哦。'
learning_reply_txt = u'恭喜你，今天完成了学习任务，离成功又近了一步。'
sport_reply_txt = u'锻炼身体，保卫自己。锻炼肌肉，防止挨揍。yeah！'
family_reply_txt = u'再忙也要抽空配配家人哦。'
challenge_reply_txt = u'少侠，等你坚持练30天剑再来比武吧。'
about_reply_txt = u''
unknow_reply_txt = u''


def replay_txt(to_user, from_user, create_time, content):
    '回复文本消息'
    tpl_txt_msg = '''
    <xml>
    <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
    <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
    <CreateTime>%(create_time)s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%(content)s]]></Content>
    </xml>
    '''

    return tpl_txt_msg % dict(from_user=to_user,
                              to_user=from_user,
                              create_time=create_time,
                              content=content)


def get_log(from_user, op):
    return web.ctx.db.query(LianjianLog).filter_by(from_user=from_user, op=op).first()


def add_log(from_user, op):
    old_log = get_log(from_user, op)
    if not old_log:  # 全新记录
        log = LianjianLog(from_user)
        log.op = op
        log.total_hits = 1
        log.keep_hits = 1
        log.created_on = datetime.now()
        web.ctx.db.add(log)
        logging.debug('add_log new log')
    else:  # 有则修改
        logging.debug("exist log:%s", old_log.__dict__)
      
        diff = datetime.now() - old_log.created_on
        # 同一天，直接返回
        if datetime.now().strftime('%Y-%m-%d') == old_log.created_on.strftime('%Y-%m-%d'):
            logging.debug('add_log return')
            return
        elif diff <= timedelta(days=2):  # 48小时内连续增加
            old_log.total_hits += 1
            old_log.keep_hits += 1
            logging.debug('add_log keep_hits += 1')
        else:
            old_log.total_hits += 1
            old_log.keep_hits = 1
            logging.debug('add_log keep_hits = 1')

    web.ctx.db.commit()


def verification_request():
    '验证请求是否来自微信'
    input = web.input()
    signature = input.signature
    timestamp = input.timestamp
    nonce = input.nonce

    tmp_str = ''.join(sorted([TOKEN, timestamp, nonce]))
    tmp_str = hashlib.sha1(tmp_str).hexdigest()

    if tmp_str == signature:
        return True
    else:
        return False


def get_menu_text(key):
    '点击菜单获取回复'
    if key == 'sleep':
        return sleep_reply_txt
    
    if key == 'happy':
        return happy_reply_txt

    if key == 'learning':
        return learning_reply_txt

    if key == 'sport':
        return sport_reply_txt

    if key == 'family':
        return family_reply_txt

    if key == 'challenge':
        return challenge_reply_txt

    if key == 'about':
        return welcom_txt

    return unknow_reply_txt


def get_txtmsg_text(from_user, msg):
    '用户输入单获取回复'
    msg = msg.strip()
    result = welcom_txt
    if msg == '#1':
        add_log(from_user, 1)
        log = get_log(from_user, 1)
        result = sleep_reply_txt
        result += u'\n该招式已经连续练习%s天，总计%s天。' % (log.keep_hits, log.total_hits)
    
    if msg == '#2':
        add_log(from_user, 2)
        log = get_log(from_user, 2)
        result = happy_reply_txt
        result += u'\n该招式已经连续练习%s天，总计%s天。' % (log.keep_hits, log.total_hits)

    if msg == '#3':
        add_log(from_user, 3)
        log = get_log(from_user, 3)
        result = learning_reply_txt
        result += u'\n该招式已经连续练习%s天，总计%s天。' % (log.keep_hits, log.total_hits)
 
    if msg == '#4':
        add_log(from_user, 4)
        log = get_log(from_user, 4)
        result = sport_reply_txt
        result += u'\n该招式已经连续练习%s天，总计%s天。' % (log.keep_hits, log.total_hits)
 
    if msg == '#5':
        add_log(from_user, 5)
        log = get_log(from_user, 5)
        result = family_reply_txt
        result += u'\n该招式已经连续练习%s天，总计%s天。' % (log.keep_hits, log.total_hits)

    if msg == '##':
        result = challenge_reply_txt

    return result


class default(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        echostr = web.input().echostr
        if verification_request():
            return echostr
        else:
            return ''

    def POST(self):
        if not verification_request():
            return u'总感觉哪里不对。1'

        root = ElementTree.fromstring(web.data())
        msg_type = root.find('MsgType').text
        to_user = root.find('ToUserName').text
        from_user = root.find('FromUserName').text
        create_time = root.find('CreateTime').text

        if msg_type == 'event':
            event = root.find('Event').text
            if event == 'CLICK':
                # 点击菜单事件
                event_key = root.find('EventKey').text
                txt = get_menu_text(event_key)
                return replay_txt(to_user, from_user, create_time, txt)
            else:
                # 其它事件，如关注，扫描二维码等
                txt = welcom_txt
                return replay_txt(to_user, from_user, create_time, txt)
        elif msg_type == 'text':
            # 输入文本消息
            msg = root.find('Content').text
            txt = get_txtmsg_text(from_user, msg)
            return replay_txt(to_user, from_user, create_time, txt)
        else:
            # 输入语音，图片等消息
            txt = welcom_txt
            return replay_txt(to_user, from_user, create_time, txt)

        # 默认回复
        txt = welcom_txt
        return replay_txt(to_user, from_user, create_time, txt)
