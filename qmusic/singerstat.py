
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

url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?_=1535461585753'

header = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'close',
    'Referer': 'https://y.qq.com/m/digitalbum/gold/index.html?_video=true&id=4359159&g_f=tuijiannewupload',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/8.6.0 Mskin/white Mcolor/31c27cff Bcolor/00000000 skinid[0] NetType/WIFI WebView/UIWebView Released[1] zh-CN DeviceModel/iPhone7,2',
    'Accept': 'application/json'
}

dataCall = {
  "comm": {
    "g_tk": 2078841671,
    "uin": 12345678,
    "format": "json",
    "inCharset": "utf-8",
    "outCharset": "utf-8",
    "notice": 0,
    "platform": "h5",
    "needNewCode": 1,
    "ct": 23,
    "cv": 0
  },
  "requestSingerTotalCallList": {
    "method": "SingerFansRankList",
    "param": {
      "actid": 279,
      "singerid": 2141375,
      "rank_type": 0,
      "start": 0,
      "num": 1
    },
    "module": "mall.AlbumCallSvr"
  },
  "requestSingerTodayCallList": {
    "method": "SingerFansRankList",
    "param": {
      "actid": 279,
      "singerid": 2141375,
      "rank_type": 1,
      "start": 0,
      "num": 1
    },
    "module": "mall.AlbumCallSvr"
  },
  
  "requestSingerInfo": {
    "method": "SingerCallInfo",
    "param": {
      "actid": 279,
      "singerid": 2141375
    },
    "module": "mall.AlbumCallSvr"
  }
}

def requestPosts(data):
    postdata = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, postdata, header)
    rsp = urllib.request.urlopen(req)
    ret = json.loads(rsp.read().decode('utf-8'))
    return ret

singers = {
  '2141375':'杨超越',
  '1530392':'Sunnee',
  '2141459':'赖美云',
  '2141458':'傅菁',
  '2141373':'段奥娟',
  '1512412':'Yamy',
  '2141386':'徐梦洁',
  '2141486':'李紫婷'
}

stats = []

for key in singers:
  singer = int(key)
  dataCall['requestSingerTotalCallList']['param']['singerid'] = singer
  dataCall['requestSingerTodayCallList']['param']['singerid'] = singer
  dataCall['requestSingerInfo']['param']['singerid'] = singer

  ret = requestPosts(dataCall)

  totalAlbum = ret['requestSingerInfo']['data']['call_num']
  todayPerson = ret['requestSingerTodayCallList']['data']['total']
  totalPerson = ret['requestSingerTotalCallList']['data']['total']

  stat = {}
  stat['singer'] = singer
  stat['name'] = singers[key]
  stat['todayPerson'] = todayPerson
  stat['totalPerson'] = totalPerson
  stat['totalAlbum'] = totalAlbum
  stat['averageAlbum'] = float('%.2f' % (totalAlbum / totalPerson))
  stats.append(stat)

stats.sort(key = lambda x:x['todayPerson'], reverse = True)

def writeToXls(xlsName, stats):
  book = xlwt.Workbook()
  ws = book.add_sheet('统计')
  ws.write(0, 0, '名字')
  ws.write(0, 1, '今日助燃人数')
  ws.write(0, 2, '总助燃人数')
  ws.write(0, 3, '总助燃数量')
  ws.write(0, 4, '人均助燃数量')

  line = 0
  for stat in stats:
      print(stat)
      line += 1
      ws.write(line, 0, stat['name'])
      ws.write(line, 1, stat['todayPerson'])
      ws.write(line, 2, stat['totalPerson'])
      ws.write(line, 3, stat['totalAlbum'])
      ws.write(line, 4, stat['averageAlbum'])
  
  book.save(xlsName)

statTime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
xlsName = 'albumstat_' + statTime + '.xls'
writeToXls(xlsName, stats)
