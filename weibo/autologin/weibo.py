#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import json
import os
import re
import requests
import sys
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

        self.proxies = {}
        self.headers = {}
        self.sid = 0

        self.session = None
        self.state = False

        self.code = -1

        self.initParams()

    def initParams(self):
        self.proxies = {
            'http': 'http://127.0.0.1:8866/',
            'https': 'http://127.0.0.1:8866/'
        }
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

    def login(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.Session()
        #self.session.verify = False
        #self.session.proxies = self.proxies
        self.session.headers = self.headers

        # 预登录
        su = util.encodeUsername(self.username)
        url = r'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)' %(su)
        rsp = self.session.get(url, headers=self.headers)

        # print('--- prelogin url ---', url, '\n', flush=True)
        # print('--- prelogin rsp ---', rsp, '\n', flush=True)

        jstring = re.findall(r'\((\{.*?\})\)', rsp.text)[0]
        preRspData = json.loads(jstring)

        print('--- prelogin rsp data ---', preRspData, '\n', flush=True)

        # 验证码
        pcid = preRspData['pcid']
        url = r'https://login.sina.com.cn/cgi/pin.php?r=69631672&s=0&p=%s' %(pcid)
        webbrowser.open_new_tab(url)

        print('--- login captcha url ---', url, '\n', flush=True)

        self.servertime = preRspData["servertime"]
        self.nonce = preRspData["nonce"]
        self.pubkey = preRspData["pubkey"]
        self.rsakv = preRspData["rsakv"]

        # 登录
        loginReqData = util.encodePostData(self.username, self.password, self.servertime, self.nonce, self.pubkey, self.rsakv)
        loginReqData['pcid'] = preRspData['pcid']
        loginReqData['door'] = input('Input captcha of url above in browser: ')

        # print('--- login req headers ---', self.headers, '\n', flush=True)
        # print('--- login req data ---', loginReqData, '\n', flush=True)

        url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        rsp = self.session.post(url, data=loginReqData, headers=self.headers)

        # print('--- login session cookies ---', session.cookies, '\n', flush=True)
        # print('--- login rsp status ---', rsp.status_code, '\n', flush=True)
        # print('--- login rsp headers ---', rsp.headers, '\n', flush=True)
        # print('--- login rsp content ---', rsp.content, '\n', flush=True)

        jstring = rsp.content.decode('utf-8')
        loginRspData = json.loads(jstring)

        print('--- login rsp data ---', loginRspData, '\n', flush=True)

        # 登录失败
        if loginRspData['retcode'] != '0':
            print('!!! login failed !!! reason: ', loginRspData['reason'])
            return False

        # 跨域处理
        for crossUrl in loginRspData['crossDomainUrlList']:
            rsp = self.session.get(crossUrl, headers=self.headers)

            # print('--- cross session cookies ---', session.cookies, '\n', flush=True)
            # print('--- cross rsp status ---', rsp.status_code, '\n', flush=True)
            # print('--- cross rsp headers ---', rsp.headers, '\n', flush=True)
            # print('--- cross rsp content ---', rsp.content, '\n', flush=True)

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

        # print('--- post req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- post rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- follow req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- follow rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- like req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- like rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- comment req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- comment rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- forward req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- forward rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- ilike req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- ilike rsp code ---', rsp.status_code, self.code, '\n', flush=True)
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

        # print('--- icomment req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- icomment rsp code ---', rsp.status_code, self.code, '\n', flush=True)
        return self

    def tfollow(self, tid):
        wtid = r'100808%s' %(tid)
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/proxy?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Content-Type'] = r'application/x-www-form-urlencoded'
        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(wtid)

        data = {
            'uid': self.sid,
            'objectid': r'1022:%s' %(wtid),
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
            'isinterest': 'true',
            'api': 'http://i.huati.weibo.com/aj/superfollow',
            'pageid': wtid,
            'reload': 1,
            '_t': 0
        }

        #print('--- tfollow req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- tfollow rsp code ---', rsp.status_code, self.code, '\n', flush=True)
        return self

    def tsignin(self, tid):
        wtid = r'100808%s' %(tid)
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/p/aj/general/button?ajwvr=6&api=http://i.huati.weibo.com/aj/super/checkin&texta=%E7%AD%BE%E5%88%B0&textb=%E5%B7%B2%E7%AD%BE%E5%88%B0&status=0&id=' + wtid + r'&location=page_100808_super_index&timezone=GMT+0800&lang=zh-cn&plat=Win32&ua=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64;%20rv:79.0)%20Gecko/20100101%20Firefox/79.0&screen=1080*1920&__rnd=' + str(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(wtid)

        rsp = self.session.get(url, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- tsignin rsp code ---', rsp.status_code, self.code, '\n', flush=True)
        return self

    def tpost(self, tid, content, picture):
        wtid = r'100808%s' %(tid)
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/p/aj/proxy?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(wtid)

        data = {
            'id': wtid,
            'domain': '100808',
            'module': 'share_topic',
            'title': '%E5%8F%91%E5%B8%96',
            'content': '',
            'api_url': 'http://i.huati.weibo.com/pcpage/super/publisher',
            'spr': '',
            'extraurl': '',
            'is_stock': '',
            'check_url': 'http%3A%2F%2Fi.huati.weibo.com%2Faj%2Fsuperpublishauth%26pageid%3D' + wtid + '%26uid%3D1764819037',
            'location': 'page_100808_super_index',
            'text': content,
            'appkey': '',
            'style_type': 1,
            'pic_id': picture,
            'tid': '',
            'pdetail': wtid,
            'mid': '',
            'isReEdit': 'false',
            'sync_wb': 0,
            'pub_source': 'page_2',
            'api': 'http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id=%s' %(wtid),
            'longtext': 1,
            'topic_id': '1022:%s' %(wtid),
            'pub_type': 'dialog',
            '_t': 0
        }

        #print('--- tpost req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- tpost rsp code ---', rsp.status_code, self.code, '\n', flush=True)
        return self

    def tcomment(self, tid, mid, content, forward):
        wtid = r'100808%s' %(tid)
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(wtid)

        data = {
            'act': 'post',
            'mid': mid,
            'uid': self.sid,
            'forward': forward,
            'isroot': 0,
            'content': content,
            'location': 'page_100808_super_index',
            'module': 'scommlist',
            'group_source': '',
            'filter_actionlog': '',
            'pdetail': wtid,
            '_t': 0
        }

        # print('--- comment req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('--- tcomment rsp code ---', rsp.status_code, self.code, '\n', flush=True)
        return self

    def tlao(self, tid, content, number):
        wtid = r'100808%s' %(tid)
        url = r'https://weibo.com/p/%s/super_index' %(wtid)

        rsp = self.session.get(url, headers=self.headers)

        mids = re.findall(r'mid=\\"(\d*?)\\"', rsp.text)

        print('--- tlao rsp mids ---', mids, '\n', flush=True)

        count = 0
        for mid in mids:
            self.tcomment(tid, mid, content, 0)
            count += 1
            if count >= number:
              break

        self.code = 100000
        return self
