
#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import sys
import time
import urllib.request
import urllib.parse
import json
import xlwt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

url = 'http://yc.static.qq.com/?service=App.StarList_ApiStarListsl7.RankingList'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'close',
    'Referer': 'http://news.qq.com/zt2018/cwei/app.htm?ADTAG=wx.pyq&listid=17&uid=151656&sid=640&have=true&appinstall=0&from=singlemessage&isappinstalled=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

params = {
  'seasonId': 17,
  'userId': ''
}

def requestPost(params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url=url, data=data, headers=headers, method='POST')
    rsp = urllib.request.urlopen(req)
    result = json.loads(rsp.read().decode('utf-8'))
    return result

result = requestPost(params)

stats = {}
stats['list'] = []
for info in result['data']['list']:
  stat = {} 
  stat['id'] = info['id']
  stat['count'] = info['count']
  print(stat)
  stats['list'].append(stat)

print(json.dumps(stats))

statTime = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
jsonName = 'topstat_' + statTime + '.json'

jsonFile = open(jsonName, 'w')
json.dump(stats, jsonFile, indent=4)
jsonFile.close()
