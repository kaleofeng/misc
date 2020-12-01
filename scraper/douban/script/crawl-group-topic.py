#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import configparser
import json
import io
import os
import pymysql
import re
import sys
import time
import urllib.request
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

headers = {
  "Content-Type": "application/x-www-form-urlencoded",
  "Connection": "close",
  "Referer": "https://www.douban.com",
  "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/8.6.0 Mskin/white Mcolor/31c27cff Bcolor/00000000 skinid[0] NetType/WIFI WebView/UIWebView Released[1] zh-CN DeviceModel/iPhone7,2",
  "Accept": "application/json"
}

# Current time, ingore seconds
now = int(time.time())
now -= now % 60

currentPath = os.path.dirname(os.path.abspath(__file__))
confPath = os.path.abspath(os.path.join(currentPath, "../conf/db.conf"))
print("DB conf path %s %s" % (currentPath, confPath), flush=True)

confDB = configparser.ConfigParser()
confDB.read(confPath)

mysqlHost    = confDB.get("mysql", "host")
mysqlPort    = confDB.get("mysql", "port")
mysqlUser    = confDB.get("mysql", "user")
mysqlPassword  = confDB.get("mysql", "password")
mysqlDB      = confDB.get("mysql", "db")
mysqlCharset   = confDB.get("mysql", "charset")
print("DB mysql info %s %s %s %s %s %s" % (mysqlHost, mysqlPort, mysqlUser, mysqlPassword, mysqlDB, mysqlCharset), flush=True)

def crawlTopicsOfGroup(groupId, starts):
  url = r'https://www.douban.com/group/%s/discussion?start=%d' % (groupId, starts)
  print(url, flush=True)

  req = urllib.request.Request(url=url, headers=headers, method='GET')
  rsp = urllib.request.urlopen(req)
  content = rsp.read().decode('utf-8')
  #print(content, flush=True)

  pattern = re.compile(r'<a href="([^\r\n]+)" title="([^\r\n]+)" class="">.*?</a>.*?<a href="([^\r\n]+)" class="">([^\r\n]+)</a>.*?class="r-count\s?">([^\r\n]*)</td>.*?class="time">([^\r\n]+)</td>', re.S | re.M)
  infoList = pattern.findall(content)
  #print(infoList, flush=True)

  topics = []

  for info in reversed(infoList):
    topic = {
      'groupId': groupId,
      'topicId': int(re.findall(r'topic/(\w+)/', info[0])[0]),
      'topicLink': info[0],
      'topicTitle': info[1],
      'authorId': re.findall(r'people/([^\r\n]+)/', info[2])[0],
      'authorLink': info[2],
      'authorName': info[3],
      'replyCount': int(info[4]) if len(info[4]) > 0 else 0,
      'publishTime': info[5]
    }

    topics.append(topic)
    print(topic, flush=True)

  return topics

def writeTopicsIntoDB(db, tableName, topics):
  cursor = db.cursor()

  # Write each record
  for topic in topics:
    sql = "REPLACE INTO %s(id, group_id, topic_id, topic_title, topic_link, author_id, author_name, author_link, reply_count, publish_time, record_time) \
      VALUES(0, '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" \
      %(tableName, topic['groupId'], topic['topicId'], topic['topicTitle'], topic['topicLink'], \
        topic['authorId'], topic['authorName'], topic['authorLink'], topic['replyCount'], topic['publishTime'], now)
    try:
      print(sql, flush=True)
      cursor.execute(sql)
      db.commit()
    except:
      db.rollback()
      print("Insert record[%s] into table[%s] error!" %(topic.topicId, tableName), '\n', flush=True)

  print("Write topics into db table[%s] done" %(tableName), '\n', flush=True)

if __name__ == "__main__":
  db = pymysql.connect(host=mysqlHost, port=int(mysqlPort), user=mysqlUser, passwd=mysqlPassword, db=mysqlDB, charset=mysqlCharset)

  groupId = 'python'
  starts = 100
  while starts >= 0:
    topics = crawlTopicsOfGroup(groupId, starts)
    writeTopicsIntoDB(db, 'tab_douban_group_topic', topics)
    starts -= 25
    time.sleep(0.1)

  db.close()
