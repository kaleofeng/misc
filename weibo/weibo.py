#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import requests
import time
import webbrowser

import util

class Weibo(object):
    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password

        self.servertime = None
        self.nonce = None
        self.pubkey = None
        self.rsakv = None

        self.headers = {}
        self.sid = 0

        self.session = None
        self.state = False

        self.code = -1

        self.initParams()

    def initParams(self):
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

    def login(self, username, password):
        self.username = username
        self.password = password

        # 预登录
        su = util.encodeUsername(self.username)
        url = r'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)' %(su)
        rsp = requests.get(url, headers = self.headers).text
        
        # print('--- prelogin url ---', url, '\n')
        # print('--- prelogin rsp ---', rsp, '\n')

        jstring = re.findall(r'\((\{.*?\})\)', rsp)[0]
        preRspData = json.loads(jstring)

        print('--- prelogin rsp data ---', preRspData, '\n')

        # 验证码
        pcid = preRspData['pcid']
        url = r'https://login.sina.com.cn/cgi/pin.php?r=69631672&s=0&p=%s' %(pcid)
        webbrowser.open_new_tab(url)
        
        print('--- login captcha url ---', url, '\n')

        self.servertime = preRspData["servertime"]
        self.nonce = preRspData["nonce"]
        self.pubkey = preRspData["pubkey"]
        self.rsakv = preRspData["rsakv"]

        # 登录
        loginReqData = util.encodePostData(self.username, self.password, self.servertime, self.nonce, self.pubkey, self.rsakv)
        loginReqData['pcid'] = preRspData['pcid']
        loginReqData['door'] = input('Input captcha of url above in browser: ')

        # print('--- login req headers ---', self.headers, '\n')
        # print('--- login req data ---', loginReqData, '\n')

        self.session = requests.Session()

        url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        rsp = self.session.post(url, data = loginReqData, headers = self.headers)

        # print('--- login session cookies ---', session.cookies, '\n')
        # print('--- login rsp status ---', rsp.status_code, '\n')
        # print('--- login rsp headers ---', rsp.headers, '\n')
        # print('--- login rsp content ---', rsp.content, '\n')

        jstring = rsp.content.decode('utf-8')
        loginRspData = json.loads(jstring)

        print('--- login rsp data ---', loginRspData, '\n')

        # 登录失败
        if loginRspData['retcode'] != '0':
            print('!!! login failed !!! reason: ', loginRspData['reason'])
            return False

        # 跨域处理
        for crossUrl in loginRspData['crossDomainUrlList']:
            rsp = self.session.get(crossUrl, headers = self.headers)

            # print('--- cross session cookies ---', session.cookies, '\n')
            # print('--- cross rsp status ---', rsp.status_code, '\n')
            # print('--- cross rsp headers ---', rsp.headers, '\n')
            # print('--- cross rsp content ---', rsp.content, '\n')

        self.sid = loginRspData['uid']
        self.state = True
        return self

    def logout(self):
        self.session.close()

    def post(self, content):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'location': 'v6_content_home',
            'text': content,
            'appkey': '',
            'style_type': 1,
            'pic_id': '',
            'tid': '',
            'pdetail': '',
            'mid': '',
            'isReEdit': False,
            'rank': 0,
            'rankid': '',
            'module': 'stissue',
            'pub_source': 'main_',
            'pub_type': 'dialog',
            'isPri': 0,
            '_t': 0
        }

        # print('--- post req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- post rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def follow(self, uid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/f/followed?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'uid': uid,
            'objectid': '',
            'f': 0,
            'extra': '',
            'refer_sort': 'friends',
            'refer_flag': '0000011002_growth_3.0_1736988591_1883659295',
            'location': 'friends_dynamic',
            'oid': self.sid,
            'wforce': 1,
            'nogroup': 1,
            'template': 2,
            'third_appkey_alias': 'attfeed',
            '_t': 0
        }

        # print('--- follow req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- follow rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def like(self, mid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/like/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'location': 'v6_content_home',
            'group_source': 'group_all',
            'version': 'mini',
            'qid': 'heart',
            'mid': mid,
            'like_src': 1,
            'cuslike': 1,
            'floating': 0,
            '_t': 0
        }

        # print('--- like req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- like rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def comment(self, mid, content, forward):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'act': 'post',
            'mid': mid,
            'uid': self.sid,
            'forward': forward,
            'isroot': 0,
            'content': content,
            'location': 'v6_content_home',
            'module': 'scommlist',
            'group_source': 'group_all',
            'pdetail': '',
            '_t': 0
        }

        # print('--- comment req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- comment rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def forward(self, mid, content, comment):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/mblog/forward?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'pic_src': '',
            'pic_id': '',
            'appkey': '',
            'mid': mid,
            'style_type': 1,
            'mark': '',
            'reason': content,
            'from_plugin': 0,
            'location': 'v6_content_home',
            'pdetail': '',
            'module': '',
            'page_module_id': '',
            'refer_sort': '',
            'is_comment_base': comment,
            'rank': 0,
            'rankid': '',
            'group_source': 'group_all',
            'isReEdit': False,
            'pdetail': '',
            '_t': 0
        }

        # print('--- forward req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- forward rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def ilike(self, rmid, iuid, imid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/like/objectlike?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'location': 'v6_content_home',
            'group_source': 'group_all',
            'commentmid': rmid,
            'o_uid': iuid,
            'object_id': imid,
            'object_type': 'comment',
            'floating': 0,
            '_t': 0
        }

        # print('--- ilike req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- ilike rsp code ---', rsp.status_code, self.code, '\n')
        return self

    def icomment(self, ruid, rmid, iuid, imid, content):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'act': 'reply',
            'mid': rmid,
            'cid': imid,
            'uid': self.sid,
            'forward': 0,
            'isroot': 0,
            'content': content,
            'ouid': iuid,
            'ispower': 1,
            'status_owner_user': ruid,
            'canUploadImage': 0,
            'canUploadFunnypic': 1,
            'module': 'scommlist',
            'dissDataFromFeed': '%5Bobject%20Object%5D',
            'approvalComment': False,
            'root_comment_id': imid,
            'location': 'v6_content_home',
            'group_source': 'group_all',
            'pdetail': '',
            '_t': 0
        }

        # print('--- icomment req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- icomment rsp code ---', rsp.status_code, self.code, '\n')
        return self
        
    def tfollow(self, tid):
        home = r'https://weibo.com/p/100808%s/super_index' %(tid)
        rsp = self.session.get(home, headers = self.headers)

        print('--- tfollow rsp ---', rsp, '\n')

        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/proxy?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Content-Type'] = r'application/x-www-form-urlencoded'
        self.headers['Referer'] = r'https://weibo.com/p/100808%s/super_index' %(tid)

        data = {
            'uid': self.sid,
            'objectid': r'1022%%3A100808%s' %(tid),
            'f': 1,
            'extra': '',
            'refer_sort': '',
            'refer_flag': '',
            'location': 'page_100808_super_index',
            'oid': tid,
            'wforce': 1,
            'nogroup': 1,
            'fnick': '',
            'template': 4,
            'isinterest': True,
            'api': 'http%3A%2F%2Fi.huati.weibo.com%2Faj%2Fsuperfollow',
            'pageid': r'100808%s' %(tid),
            'reload': 1,
            '_t': 0
        }

        print('--- tfollow req data ---', data, '\n')

        rsp = self.session.post(url, data = data, headers = self.headers)

        self.code = int(re.findall('code":"(.*?)"', rsp.text)[0])

        print('--- tfollow rsp code ---', rsp.status_code, self.code, '\n')
        print('--- tfollow rsp code ---', rsp.text, '\n')
        return self
        
    def tsignin(self, tid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/p/aj/general/button?ajwvr=6&api=http://i.huati.weibo.com/aj/super/checkin&texta=%E7%AD%BE%E5%88%B0&textb=%E5%B7%B2%E7%AD%BE%E5%88%B0&status=0&id=%s&location=page_100808_super_index&__rnd=%s' %(tid, timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/100808%s/super_index' %(tid)

        rsp = session.get(url, headers = self.headers)

        print('--- tsignin rsp code ---', rsp.status_code, self.code, '\n')
        return self
