
#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import sys
import urllib.request
import urllib.parse
import json
import time
import xlwt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

def requestGet(url):
    req = urllib.request.Request(url)
    rsp = urllib.request.urlopen(req)
    ret = json.loads(rsp.read().decode('utf-8'))
    return ret

def filterNick(nick):
    try:
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'', nick)

stats = []

def requestSingerFans(todayTotal):
    global stats

    begin = 0
    end = 99
    patchCount = 100

    while end < todayTotal:
        print("---------------", begin, end, todayTotal)

        url = 'https://c.y.qq.com/shop/fcgi-bin/fcg_album_rank?g_tk=1330568935&uin=12345678&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&ct=23&cv=0&begin='
        url += str(begin)
        url += '&end='
        url += str(end)
        url += '&rankname=uin_rank_peract_352_day&_=1535634979229'
        ret = requestGet(url)

        stats += ret['data']['uin_rank_peract_352_day']

        begin += patchCount
        end += patchCount

requestSingerFans(500)

book = xlwt.Workbook()
ws = book.add_sheet('统计')
ws.write(0, 0, '排名')
ws.write(0, 1, '昵称')
ws.write(0, 2, '总助燃数量')

line = 0
stats.sort(key = lambda x:x['iScore'], reverse = True)
for stat in stats:
    print(stat)
    line += 1
    ws.write(line, 0, stat['iRank'])
    ws.write(line, 1, stat['strNick'])
    ws.write(line, 2, stat['iScore'])

statTime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
xlsName = 'data/peracttoday_' + statTime + '.xls'
book.save(xlsName)
