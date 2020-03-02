
#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import json
import re
import sched
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

header = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'close',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/8.6.0 Mskin/white Mcolor/31c27cff Bcolor/00000000 skinid[0] NetType/WIFI WebView/UIWebView Released[1] zh-CN DeviceModel/iPhone7,2',
    'Accept': 'application/json'
}

def requestGet(url):
    req = urllib.request.Request(url)
    rsp = urllib.request.urlopen(req)
    return rsp.read().decode('utf-8')

def requestPost(url, headers, params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url=url, headers=headers, data=data, method='POST')
    rsp = urllib.request.urlopen(req)
    return rsp.read().decode('utf-8')

serviceHost = 'https://www.metazion.net/'
ridUrl = serviceHost + '/misc/id/uuid'
billboardUrl = serviceHost + '/billboard/save'

ridData = requestGet(ridUrl)
ridJson = json.loads(ridData)
print(ridJson, flush=True)

rid = ridJson['uuid']
print(rid, flush=True)

rid = 'a29ac5771ba94758b3f223a9b35cb306'

schedule = sched.scheduler(time.time, time.sleep)

def checkAndSaveIp(interval):
    print('checkAndSaveIp', interval, flush=True)

    ipUrl = 'http://ifconfig.me/ip'
    ipData = requestGet(ipUrl)
    print(ipData, flush=True)

    billboardData = {}
    billboardData['rid'] = rid
    billboardData['value'] = ipData

    ret = requestPost(billboardUrl, header, billboardData)
    print(ret, flush=True)

    schedule.enter(interval, 0, checkAndSaveIp, (interval,))

def startSchedule(interval):
    schedule.enter(0, 0, checkAndSaveIp, (interval,))
    schedule.run()

startSchedule(10)
