#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import json
import os
import pymysql
import re
import requests
import sys
import time

import wbcrawl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Current time, ingore seconds
now = int(time.time())
now -= now % 60

def writePostsIntoDB(tableName, posts):
    db = pymysql.connect(host='workstation', port=3306, user='root', passwd='123456', db='tool', charset='utf8mb4')
    cursor = db.cursor()

    # Write each record
    for post in posts:
        sql = "REPLACE INTO %s VALUES(0, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
            %(tableName, post.pid, post.ptext, post.created_at, post.reposts_count, post.comments_count, post.attitudes_count,
            post.author.uid, post.author.uname, post.author.gender, post.author.urank,
            post.author.followers_count, post.author.follow_count, now)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            print("Insert record[%s] into table[%s] error!" %(post.pid, tableName), '\n', flush=True)

    db.close()
    print("Write posts into db table[%s] done" %(tableName), '\n', flush=True)

if __name__ == '__main__':
    dstUids = [
        2726672453,
        2871033210,
        5142840067,
        5255814135,
        5305078356,
        5601456932,
        5735084779,
        5874584452,
        6274465503]

    for dstUid in dstUids:
        blogger = wbcrawl.Blogger(dstUid)
        keywords = ['热巴', 'dlrb']

        weibo = wbcrawl.Weibo()
        weibo.crawlPosts(blogger, keywords)

        writePostsIntoDB('tab_posts', blogger.posts)
