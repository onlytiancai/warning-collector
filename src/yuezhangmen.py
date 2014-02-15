# -*- coding: utf-8 -*-
import web
import hashlib
from xml.etree import ElementTree

TOKEN = '855dde440a874ef798227147f6686f55'


def replay_txt(to_user, from_user, create_time, content):
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


def verification_request():
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
    if key == 'sleep':
        return u'只有充足良好的睡眠，才能做好事情。'
    
    if key == 'happy':
        return u'无论什么时候，都要保持好的心情，否则啥事情都做不好。'

    if key == 'learning':
        return u'每天至少要学习半小时，不然就落后啦。'

    if key == 'sport':
        return u'健康的身体才是做任何事情的本钱。'

    if key == 'family':
        return u'每天花时间陪陪家人哦，否则改变世界又有什么用呢？'

    if key == 'challenge':
        return u'少侠，最少要坚持练剑30天才能来比武，呵呵。'

    if key == 'about':
        return u'改变世界，从改变自己开始，从现在开始每天\"练剑\"吧。'

    return u'总感觉哪里不对。2'


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
                event_key = root.find('EventKey').text
                txt = get_menu_text(event_key)
                return replay_txt(to_user, from_user, create_time, txt)
            else:
                txt = u'改变世界，从改变自己开始，从现在开始每天\"练剑\"吧。1'
                return replay_txt(to_user, from_user, create_time, txt)
        else:
            txt = u'改变世界，从改变自己开始，从现在开始每天\"练剑\"吧。2'
            return replay_txt(to_user, from_user, create_time, txt)

        txt = u'改变世界，从改变自己开始，从现在开始每天\"练剑\"吧。3'
        return replay_txt(to_user, from_user, create_time, txt)
