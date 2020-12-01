
#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import sys
import time
import re
import urllib.request
import urllib.parse
import json
import xlwt
import pymysql

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
    "g_tk": 1330568935,
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
  "requestSingerCallList": {
    "method": "SingerFansRankList",
    "param": {
      "actid": 352,
      "singerid": 2141375,
      "rank_type": 0,
      "start": 0,
      "num": 3
    },
    "module": "mall.AlbumCallSvr"
  }
}

def filterEmoji(text):
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(u'', text)

def requestPost(data):
    postdata = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, postdata, header)
    rsp = urllib.request.urlopen(req)
    ret = json.loads(rsp.read().decode('utf-8'))
    return ret

def requestSingerCalls(data, singer, period, result):
    todayTotal = 500
    patchCount = 100
    start = 0

    data['requestSingerCallList']['param']['singerid'] = singer
    data['requestSingerCallList']['param']['rank_type'] = period

    while start < todayTotal:
        print("---------------", start, todayTotal)
        data['requestSingerCallList']['param']['start'] = start
        data['requestSingerCallList']['param']['num'] = patchCount

        ret = requestPost(data)

        singerCallsData = ret['requestSingerCallList']['data']
        result += singerCallsData['ranklist']

        todayTotal = min(todayTotal, singerCallsData['total'])
        start += patchCount

singer = 2141375

singerCallsTotal = []
requestSingerCalls(dataCall, singer, 0, singerCallsTotal)
singerCallsTotal.sort(key = lambda x: x['rank'])

singerCallsToday = []
requestSingerCalls(dataCall, singer, 1, singerCallsToday)
singerCallsToday.sort(key = lambda x: x['rank'])

def filterNick(stats):
    for stat in stats:
        stat['nick'] = filterEmoji(stat['nick'])

# filterNick(singerCallsTotal)
# filterNick(singerCallsToday)

def writeToXls(xlsName, stats):
  book = xlwt.Workbook()
  ws = book.add_sheet('统计')
  ws.write(0, 0, '排名')
  ws.write(0, 1, '助燃数量')
  ws.write(0, 2, '昵称')
  ws.write(0, 3, 'UIN')
  ws.write(0, 4, '头像')

  line = 0
  for stat in stats:
      print(stat)
      line += 1
      ws.write(line, 0, stat['rank'])
      ws.write(line, 1, stat['call_num'])
      ws.write(line, 2, stat['nick'])
      ws.write(line, 3, str(stat['uin']))
      ws.write(line, 4, stat['pic'])

  book.save(xlsName)

def writeToDB(tableName, singerCalls):
    db = pymysql.connect(host ='192.168.31.102', user = 'root', passwd = 'Root!123456', db = 'album', charset = 'utf8mb4')
    cursor = db.cursor()

    # sql = 'TRUNCATE %s' % tableName
    # try:
    #     cursor.execute(sql)
    #     db.commit()
    # except:
    #     db.rollback()
    #     print('truncate table error')

    recordTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    for sct in singerCalls:
        print(sct['rank'], sct['call_num'], sct['nick'], sct['pic'])
        sql = "REPLACE INTO %s VALUES('%d', '%d', '%d', '%d', '%s', '%s', '%s')" % (tableName, singer, sct['rank'], sct['call_num'], sct['uin'], sct['nick'], sct['pic'], recordTime)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            print('insert error')

    db.close()

statTime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))

xlsTotal = 'data/fanstotal_%s_%s.xls' % (singer, statTime)
writeToXls(xlsTotal, singerCallsTotal)

xlsToday = 'data/fanstoday_%s_%s.xls' % (singer, statTime)
writeToXls(xlsToday, singerCallsToday)

#writeToDB('tab_album_total', singerCallsTotal)
#writeToDB('tab_album_today', singerCallsToday)
