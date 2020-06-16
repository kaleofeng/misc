#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import configparser
import jieba
import jieba.posseg
import jieba.analyse
import json
import io
import os
import pymysql
import re
import sys
import time
import urllib.request
import urllib.parse
import wordcloud

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Current time, ingore seconds
now = int(time.time())
now -= now % 60

currentPath = os.path.dirname(os.path.abspath(__file__))
confPath = os.path.abspath(os.path.join(currentPath, '../conf/db.conf'))
print('DB conf path %s %s' % (currentPath, confPath), flush=True)

confDB = configparser.ConfigParser()
confDB.read(confPath)

mysqlHost       = confDB.get('mysql', 'host')
mysqlPort       = confDB.get('mysql', 'port')
mysqlUser       = confDB.get('mysql', 'user')
mysqlPassword   = confDB.get('mysql', 'password')
mysqlDB         = confDB.get('mysql', 'db')
mysqlCharset    = confDB.get('mysql', 'charset')
print('DB mysql info %s %s %s %s %s %s' % (mysqlHost, mysqlPort, mysqlUser, mysqlPassword, mysqlDB, mysqlCharset), flush=True)

def readTopicsFromDB(tableName, number, topics):
  db = pymysql.connect(host=mysqlHost, port=int(mysqlPort), user=mysqlUser, passwd=mysqlPassword, db=mysqlDB, charset=mysqlCharset)
  cursor = db.cursor()

  # Read some record
  sql = 'SELECT topic_title FROM %s ORDER BY id DESC LIMIT %d' %(tableName, number)
  try:
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
      topicTitle = row[0]
      topics.append(topicTitle)
  except:
    print('Select records from table[%s] error!' %(tableName), '\n', flush=True)

  print('Read posts from db table[%s] done' %(tableName), '\n', flush=True)
  db.close()

def writeTopicsIntoFile(filePath, topics):
  with open(filePath, 'w+', encoding='utf-8') as f:
    for topic in topics:
      f.write(topic + '\n')

def generateWordCloud(srcFilePath, dstFilePath):
  with open(srcFilePath, encoding='utf-8') as f:
    text = f.read()

    textlist = jieba.lcut(text)
    string = " ".join(textlist)

    wc = wordcloud.WordCloud(width=1000, height=800, background_color='white', font_path='msyh.ttc')
    wc.generate(string)
    wc.to_file(dstFilePath)

topics = []
readTopicsFromDB('tab_douban_group_topic', 1000000, topics)
writeTopicsIntoFile('data/group-topic.txt', topics)
generateWordCloud('data/group-topic.txt', 'data/group-topic2.png')
