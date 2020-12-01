#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import json
import pymysql
import sys
import time
import urllib.parse
import urllib.request
import xlwt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

url = "https://u.y.qq.com/cgi-bin/musicu.fcg?_=1535461585753"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "close",
    "Referer": "https://y.qq.com/m/digitalbum/gold/index.html?_video=true&id=4359159&g_f=tuijiannewupload",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/8.6.0 Mskin/white Mcolor/31c27cff Bcolor/00000000 skinid[0] NetType/WIFI WebView/UIWebView Released[1] zh-CN DeviceModel/iPhone7,2",
    "Accept": "application/json"
}

params = {
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

def requestPost(url, headers, params):
    data = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(url=url, headers=headers, data=data, method='POST')
    rsp = urllib.request.urlopen(req)
    result = json.loads(rsp.read().decode('utf-8'))
    return result

albums = {
    "279": "撞",
    "352": "立风"
}

singers = {
    "1527896": "孟美岐",
    "2141217": "吴宣仪",
    "2141375": "杨超越",
    "2141373": "段奥娟",
    "1512412": "Yamy",
    "2141459": "赖美云",
    "2141439": "张紫宁",
    "1530392": "Sunnee",
    "2141386": "徐梦洁",
    "2141458": "傅菁",
    "2141486": "李紫婷"
}

stats = []

for ka in albums:
    album = int(ka)
    for ks in singers:
        singer = int(ks)
        params["requestSingerTotalCallList"]["param"]["actid"] = album
        params["requestSingerTotalCallList"]["param"]["singerid"] = singer
        params["requestSingerTodayCallList"]["param"]["actid"] = album
        params["requestSingerTodayCallList"]["param"]["singerid"] = singer
        params["requestSingerInfo"]["param"]["actid"] = album
        params["requestSingerInfo"]["param"]["singerid"] = singer

        ret = requestPost(url, headers, params)

        totalAlbums = ret["requestSingerInfo"]["data"]["call_num"]
        todayPersons = ret["requestSingerTodayCallList"]["data"]["total"]
        totalPersons = ret["requestSingerTotalCallList"]["data"]["total"]

        stat = {}
        stat["album"] = album
        stat["albumName"] = albums[ka]
        stat["singer"] = singer
        stat["singerName"] = singers[ks]
        stat["todayPersons"] = todayPersons
        stat["totalPersons"] = totalPersons
        stat["totalAlbums"] = totalAlbums
        stat["averageAlbum"] = float("%.2f" % (totalAlbums / totalPersons))
        stats.append(stat)

# Current time, ingore seconds
now = int(time.time())
now -= now % 60

def writeIntoFile(xlsName, stats):
    book = xlwt.Workbook()
    ws = book.add_sheet("统计")
    ws.write(0, 0, "专辑ID")
    ws.write(0, 1, "歌手ID")
    ws.write(0, 2, "歌手名字")
    ws.write(0, 3, "今日助燃人数")
    ws.write(0, 4, "总助燃人数")
    ws.write(0, 5, "总助燃数量")

    line = 0
    for stat in stats:
        line += 1
        ws.write(line, 0, stat["album"])
        ws.write(line, 1, stat["albumName"])
        ws.write(line, 2, stat["singer"])
        ws.write(line, 3, stat["singerName"])
        ws.write(line, 4, stat["todayPersons"])
        ws.write(line, 5, stat["totalPersons"])
        ws.write(line, 6, stat["totalAlbums"])
        print(stat)

    book.save(xlsName)
    print("Write into file xls[%s] done" % xlsName)

statTime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(now))
xlsName = "data/qmusic_singerstat_" + statTime + ".xls"
writeIntoFile(xlsName, stats)

def writeIntoDB(tableName, stats):
    db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="tool", charset="utf8mb4")
    cursor = db.cursor()

    # Write each record
    for stat in stats:
        sql = "INSERT INTO %s VALUES(0, '%d', '%d', '%s', '%d', '%d', '%d', '%d')" % (tableName, stat["album"], stat["singer"], stat["singerName"], stat["todayPersons"], stat["totalPersons"], stat["totalAlbums"], now)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            print("Insert record[%d] error!" % stat["singer"])

    db.close()
    print("Write into db table[%s] done" % tableName)

writeIntoDB("tab_qmusic_singerstat", stats)
