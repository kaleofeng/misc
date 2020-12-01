#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.cookiejar as cookiejar
import io
import json
import os
import re
import requests
import sys
import time

import captcha
import util

class Weibo(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.sid = 0

        self.servertime = None
        self.nonce = None
        self.pubkey = None
        self.rsakv = None

        self.proxies = {}
        self.headers = {}

        self.session = None
        self.state = False

        self.code = -1

        self.initParams()

    def initParams(self):
        self.proxies = {
            'http': 'http://127.0.0.1:8866/',
            'https': 'http://127.0.0.1:8866/'
        }
        self.headers['Referer'] = 'https://weibo.com/'
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'

    def login(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.Session()
        #self.session.verify = False
        #self.session.proxies = self.proxies
        self.session.headers = self.headers
        self.session.cookies = cookiejar.LWPCookieJar(filename="data/cookies.txt")

        # 尝试使用cookie登录
        try:
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)
            home = r'https://weibo.com'
            rsp = self.session.get(home)

            # print('--- login by cookie rsp ---', rsp, '\n', flush=True)

            uids = re.findall(r"CONFIG\['uid'\]='(\d*?)'", rsp.text)
            if len(uids) < 1:
                raise ValueError

            self.sid = uids[0]
            self.state = True

            print('Login by cookie success', self.sid, self.state, '\n', flush=True)
            return self
        except:
            print('Login by cookie load failed!', '\n', flush=True)

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
        captchaUrl = r'https://login.sina.com.cn/cgi/pin.php?r=69631672&s=0&p=%s' %(pcid)

        print('--- login captcha url ---', captchaUrl, '\n', flush=True)

        # 本地手动输入验证码
        captchaText = captcha.identifyLocal(captchaUrl)

        # # 远程人工识别验证码
        # captchaText = captcha.identifyRemote(captchaUrl)

        print('--- login captcha text ---', captchaText, '\n', flush=True)

        # 其他数据
        self.servertime = preRspData["servertime"]
        self.nonce = preRspData["nonce"]
        self.pubkey = preRspData["pubkey"]
        self.rsakv = preRspData["rsakv"]

        # 登录
        loginReqData = util.encodePostData(self.username, self.password, self.servertime, self.nonce, self.pubkey, self.rsakv)
        loginReqData['pcid'] = preRspData['pcid']
        loginReqData['door'] = captchaText

        print('--- login req headers ---', self.headers, '\n', flush=True)
        # print('--- login req data ---', loginReqData, '\n', flush=True)

        url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        rsp = self.session.post(url, data=loginReqData, headers=self.headers)

        # print('--- login session cookies ---', self.session.cookies, '\n', flush=True)
        # print('--- login rsp status ---', rsp.status_code, '\n', flush=True)
        # print('--- login rsp headers ---', rsp.headers, '\n', flush=True)
        # print('--- login rsp content ---', rsp.content, '\n', flush=True)

        loginRspData = json.loads(rsp.content)

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
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)

        print('Login by account success', self.sid, self.state, '\n', flush=True)
        return self

    def logout(self):
        self.session.close()

    def post(self, text):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'location': 'v6_content_home',
            'text': text,
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

        print('Post rsp code: ', rsp.status_code, self.code, '\n', flush=True)
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

        print('Follow rsp code: ', rsp.status_code, self.code, '\n', flush=True)
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

        print('Like rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def comment(self, mid, text, forward):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'http://weibo.com/u/%s?wvr=5&lf=reg' %(self.sid)

        data = {
            'act': 'post',
            'mid': mid,
            'uid': self.sid,
            'forward': forward,
            'isroot': 0,
            'content': text,
            'location': 'v6_content_home',
            'module': 'scommlist',
            'group_source': 'group_all',
            'pdetail': '',
            '_t': 0
        }

        # print('--- comment req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('Cmment rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def forward(self, mid, text, comment):
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
            'reason': text,
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

        print('Forward rsp code: ', rsp.status_code, self.code, '\n', flush=True)
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

        print('I Like rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def icomment(self, ruid, rmid, iuid, imid, text):
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
            'content': text,
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

        print('I Comment rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def hfollow(self, hid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/proxy?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(hid)

        data = {
            'uid': self.sid,
            'objectid': r'1022:%s' %(hid),
            'f': 1,
            'extra': '',
            'refer_sort': '',
            'refer_flag': '',
            'location': 'page_100808_super_index',
            'oid': hid[6:],
            'wforce': 1,
            'nogroup': 1,
            'fnick': '',
            'template': 4,
            'isinterest': 'true',
            'api': 'http://i.huati.weibo.com/aj/superfollow',
            'pageid': hid,
            'reload': 1,
            '_t': 0
        }

        #print('--- hfollow req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('H Follow rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def hsignin(self, hid):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/p/aj/general/button?ajwvr=6&api=http://i.huati.weibo.com/aj/super/checkin&texta=%E7%AD%BE%E5%88%B0&textb=%E5%B7%B2%E7%AD%BE%E5%88%B0&status=0&id=' + hid + r'&location=page_100808_super_index&timezone=GMT+0800&lang=zh-cn&plat=Win32&ua=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64;%20rv:79.0)%20Gecko/20100101%20Firefox/79.0&screen=1080*1920&__rnd=' + str(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(hid)

        rsp = self.session.get(url, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('H Signin rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def hpost(self, hid, text, picture):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/p/aj/proxy?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(hid)

        data = {
            'id': hid,
            'domain': '100808',
            'module': 'share_topic',
            'title': '%E5%8F%91%E5%B8%96',
            'content': '',
            'api_url': 'http://i.huati.weibo.com/pcpage/super/publisher',
            'spr': '',
            'extraurl': '',
            'is_stock': '',
            'check_url': 'http%3A%2F%2Fi.huati.weibo.com%2Faj%2Fsuperpublishauth%26pageid%3D' + hid + '%26uid%3D1764819037',
            'location': 'page_100808_super_index',
            'text': text,
            'appkey': '',
            'style_type': 1,
            'pic_id': picture,
            'tid': '',
            'pdetail': hid,
            'mid': '',
            'isReEdit': 'false',
            'sync_wb': 0,
            'pub_source': 'page_2',
            'api': 'http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id=%s' %(hid),
            'longtext': 1,
            'topic_id': '1022:%s' %(hid),
            'pub_type': 'dialog',
            '_t': 0
        }

        #print('--- hpost req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('H Post rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def hcomment(self, hid, mid, text, forward):
        timestamp = int(time.time()) * 1000
        url = r'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%s' %(timestamp)

        self.headers['Referer'] = r'https://weibo.com/p/%s/super_index' %(hid)

        data = {
            'act': 'post',
            'mid': mid,
            'uid': self.sid,
            'forward': forward,
            'isroot': 0,
            'content': text,
            'location': 'page_100808_super_index',
            'module': 'scommlist',
            'group_source': '',
            'filter_actionlog': '',
            'pdetail': hid,
            '_t': 0
        }

        # print('--- comment req data ---', data, '\n', flush=True)

        rsp = self.session.post(url, data=data, headers=self.headers)
        self.code = util.responseCode(rsp.text)

        print('H Comment rsp code: ', rsp.status_code, self.code, '\n', flush=True)
        return self

    def hsalvage(self, hid, text, number, commentThreshold):
        url = r'https://m.weibo.cn/api/container/getIndex'

        sinceId = 0
        midList = []
        commentsCountList = []

        while len(midList) < number:
          params = {
            'containerid': '%s_-_sort_time' %(hid),
            'luicode': '10000011',
            'lfid': hid,
            'since_id': sinceId
          }

          rsp = self.session.get(url, params=params, headers=self.headers)

          # print('--- hsalvage rsp text ---', rsp.text, '\n', flush=True)

          sinceIds = re.findall(r'"since_id":(\d*?),', rsp.text)
          mids = re.findall(r'"mid":"(\d*?)"', rsp.text)
          commentsCounts = re.findall(r'"comments_count":(\d*?),', rsp.text)

          # print('H Salvage rsp sinceIds: ', sinceIds, '\n', flush=True)
          # print('H Salvage rsp mids: ', mids, '\n', flush=True)
          # print('H Salvage rsp commentsCounts: ', commentsCounts, '\n', flush=True)

          sinceIdNumber = len(sinceIds)
          if len(sinceIds) < 1:
            # print('--- hsalvage no sinceId ---', sinceIdNumber, '\n', flush=True)
            break

          sinceId = sinceIds[0]

          midNumber = len(mids)
          commentsCountNumber = len(commentsCounts)
          if midNumber != commentsCountNumber or midNumber < 1:
            # print('--- hsalvage count mismatch ---', midNumber, commentsCountNumber, '\n', flush=True)
            break

          for i in range(midNumber):
            mid = mids[i]
            commentsCount = commentsCounts[i]
            # print('--- hsalvage mid commentsCount ---', mid, commentsCount, '\n', flush=True)

            if commentThreshold < 0 or int(commentsCount) < commentThreshold:
              midList.append(mid)
              commentsCountList.append(commentsCount)

        # print('H Salvage rsp midList: ', midList, '\n', flush=True)
        # print('H Salvage rsp commentsCountList: ', commentsCountList, '\n', flush=True)

        count = 0
        for mid in midList:
            self.hcomment(hid, mid, text, 0)
            count += 1
            if count >= number:
              break

        self.code = 100000
        return self
