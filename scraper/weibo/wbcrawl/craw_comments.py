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

def readPostsFromDB(tableName, number, posts):
    db = pymysql.connect(host='workstation', port=3306, user='root', passwd='123456', db='tool', charset='utf8mb4')
    cursor = db.cursor()

    # Read some record
    sql = "SELECT * FROM %s ORDER BY id DESC LIMIT %d" %(tableName, number)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            post = wbcrawl.Post()
            post.pid = row[1]
            post.ptext = row[2]
            post.created_at = row[3]
            post.reposts_count = row[4]
            post.comments_count = row[5]
            post.attitudes_count = row[6]
            post.author.uid = row[7]
            post.author.uname = row[8]
            print("Read post done", post, '\n', flush=True)
            posts.append(post)
    except:
        print("Select records from table[%s] error!" %(tableName), '\n', flush=True)

    print("Read posts from db table[%s] done" %(tableName), '\n', flush=True)
    db.close()
    posts.reverse()

def writeCommentsIntoDB(tableName, post):
    db = pymysql.connect(host='workstation', port=3306, user='root', passwd='123456', db='tool', charset='utf8mb4')
    cursor = db.cursor()

    # Write each record
    for comment in post.comments:
        sql = "INSERT INTO %s VALUES(0, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', \
            '%s', '%s')" \
            %(tableName, comment.cid, comment.ctext, comment.created_at, comment.total_number, comment.like_count,
            comment.isLikedByMblogAuthor, comment.cindex, post.pid,
            comment.author.uid, comment.author.uname, comment.author.gender, comment.author.urank,
            comment.author.followers_count, comment.author.follow_count, now)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            print("Execute sql[%s] error!" %(sql), '\n', flush=True)

    db.close()
    print("Write comments into db table[%s] done" %(tableName), '\n', flush=True)

if __name__ == '__main__':
    blogger = wbcrawl.Blogger(0)
    keywords = ['创3', 'ycy', '杨超越']

    weibo = wbcrawl.Weibo()

    posts = []
    readPostsFromDB('tab_posts', 20, posts)
    print("posts", posts, '\n', flush=True)

    for post in posts:
        print("post", post, '\n', flush=True)
        weibo.crawlComments(post)
        writeCommentsIntoDB('tab_comments', post)
