# -*- coding: utf-8 -*-
import web
import hashlib

TOKEN = '855dde44-0a87-4ef7-9822-7147f6686f55'


class default(object):
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        input = web.input()
        signature = input.signature
        timestamp = input.timestamp
        nonce = input.nonce
        echostr = input.echostr

        tmp_str = ''.join(sorted([TOKEN, timestamp, nonce]))
        tmp_str = hashlib.sha1(tmp_str).hexdigest()

        if tmp_str == signature:
            return echostr
        else:
            return ''


