#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import json
import os
import re
import requests
import sys
import time

def checkKeywords(text, keywords):
    for keyword in keywords:
        if text.find(keyword) != -1:
            return True
    return False

def purifyText(text):
    pat = re.compile('<[^>]+>', re.S)
    return pat.sub('', text)

def normalizeDatetime(str):
    timeArray  = time.strptime(str, '%a %b %d %H:%M:%S %z %Y')
    return int(time.mktime(timeArray))

class Blogger(object):
    def __init__(self, id):
        self.id = id
        self.user = User()
        self.posts = []

    def print(self):
        print('blogger id: ', self.id, '\n', flush=True)
        print('blogger user: ', self.user, '\n', flush=True)

        for post in self.posts:
            print('blogger post: ', self.id, post, '\n', flush=True)

            for comment in post.comments:
                print('blogger post comment: ', self.id, post.pid, comment, '\n', flush=True)

                for remark in comment.remarks:
                    print('blogger post comment remark: ', self.id, post.pid, comment.cid, remark, '\n', flush=True)

class User(object):
    def __init__(self):
        self.uid = 0
        self.uname = ''
        self.gender = ''
        self.urank = 0
        self.followers_count = 0
        self.follow_count = 0

    def __str__(self):
        attrs = ", ".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())
        return "[{}: {}]".format(self.__class__.__name__, attrs)

    def fromJsonData(self, jsonData):
        self.uid = jsonData['id']
        self.uname = jsonData['screen_name']
        self.gender = jsonData['gender']
        self.urank = jsonData['urank']
        self.followers_count = jsonData['followers_count']
        self.follow_count = jsonData['follow_count']

class Post(object):
    def __init__(self):
        self.pindex = 0
        self.pid = 0
        self.ptext = ''
        self.created_at = 0
        self.reposts_count = 0
        self.comments_count = 0
        self.attitudes_count = 0
        self.author = User()
        self.comments = []

    def __str__(self):
        attrs = ", ".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())
        return "[{}: {}]".format(self.__class__.__name__, attrs)

    def fromJsonData(self, jsonData):
        self.pid = jsonData['id']
        self.ptext = purifyText(jsonData['text'])
        self.created_at = normalizeDatetime(jsonData['created_at'])
        self.reposts_count = jsonData['reposts_count']
        self.comments_count = jsonData['comments_count']
        self.attitudes_count = jsonData['attitudes_count']
        self.author.fromJsonData(jsonData['user'])

class Comment(object):
    def __init__(self):
        self.cindex = 0
        self.cid = 0
        self.ctext = ''
        self.created_at = 0
        self.total_number = 0
        self.like_count = 0
        self.isLikedByMblogAuthor = 0
        self.author = User()
        self.remarks = []

    def __str__(self):
        attrs = ", ".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())
        return "[{}: {}]".format(self.__class__.__name__, attrs)

    def fromJsonData(self, jsonData):
        self.cid = jsonData['id']
        self.ctext = purifyText(jsonData['text'])
        self.created_at = normalizeDatetime(jsonData['created_at'])
        self.total_number = jsonData['total_number']
        self.like_count = jsonData['like_count']
        self.isLikedByMblogAuthor = jsonData['isLikedByMblogAuthor']
        self.author.fromJsonData(jsonData['user'])

class Remark(object):
    def __init__(self):
        self.rindex = 0
        self.rid = 0
        self.rtext = ''
        self.created_at = 0
        self.like_count = 0
        self.author = User()

    def __str__(self):
        attrs = ", ".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())
        return "[{}: {}]".format(self.__class__.__name__, attrs)

    def fromJsonData(self, jsonData):
        self.rid = jsonData['id']
        self.rtext = purifyText(jsonData['text'])
        self.created_at = normalizeDatetime(jsonData['created_at'])
        self.like_count = jsonData['like_count']
        self.author.fromJsonData(jsonData['user'])

class Weibo(object):
    def __init__(self):
        self.headers = {}
        self.postNumber = 10
        self.commentNumber = 20
        self.remarkNumber = 3
        self.initParams()

    def initParams(self):
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

    def crawl(self, blogger, keywords):
        print('--- crawl blogger ---', blogger.id, keywords, '\n', flush=True)

        self.crawlPosts(blogger, keywords)

        for post in blogger.posts:
            self.crawlComments(post)

            for comment in post.comments:
                self.crawlRemarks(comment)

    def crawlPosts(self, blogger, keywords):
        print('--- crawlPosts blogger ---', blogger.id, keywords, self.postNumber, '\n', flush=True)

        url = r'https://m.weibo.cn/profile/info?uid=%s' %(blogger.id)
        rsp = requests.get(url, headers = self.headers)

        jsonString = rsp.content.decode('utf-8')
        jsonData = json.loads(jsonString)
        #print('--- crawlPosts rsp data ---', jsonData, '\n', flush=True)

        ok = jsonData['ok']
        if ok != 1:
            print('--- crawlPosts failed...', ok, '\n', flush=True)
            return

        payload = jsonData['data']
        userData = payload['user']
        postDatas = payload['statuses']

        blogger.user.fromJsonData(userData)

        index = 0
        for postData in postDatas:
            index += 1
            if index > self.postNumber:
                break

            post = Post()
            post.fromJsonData(postData)
            self.crawlPost(post)
            if not checkKeywords(post.ptext, keywords):
                continue

            post.pindex = index
            blogger.posts.append(post)
            #print('--- crawlPosts blogger post ---', post, '\n', flush=True)

    def crawlPost(self, post):
        print('--- crawlPost post ---', post.pid, '\n', flush=True)

        url = r'https://m.weibo.cn/statuses/extend?id=%s' %(post.pid)
        rsp = requests.get(url, headers = self.headers)

        jsonString = rsp.content.decode('utf-8')
        if jsonString.find('data') == -1:
            print('--- crawlPost post no detail ---', post.pid, '\n', flush=True)
            return

        jsonData = json.loads(jsonString)
        #print('--- crawlPost rsp data ---', jsonData, '\n', flush=True)

        ok = jsonData['ok']
        if ok != 1:
            print('--- crawlPost failed...', ok, '\n', flush=True)
            return

        payload = jsonData['data']
        postText = payload['longTextContent']
        post.ptext = purifyText(postText)

    def crawlComments(self, post):
        print('--- crawlComments post ---', post.pid, post.comments_count, self.commentNumber, '\n', flush=True)

        # if not post.child:
        #     print('--- crawlComments post no comments ---', post.pid, post.comments_count, '\n', flush=True)
        #     return

        url = r'https://m.weibo.cn//comments/hotflow?id=%s&mid=%s&max_id_type=0' %(post.pid, post.pid)
        rsp = requests.get(url, headers = self.headers)

        jsonString = rsp.content.decode('utf-8')
        if jsonString.find('data') == -1:
            print('--- crawlComments post no comments ---', post.pid, post.comments_count, '\n', flush=True)
            return

        jsonData = json.loads(jsonString)
        #print('--- crawlComments rsp data ---', jsonData, '\n', flush=True)

        ok = jsonData['ok']
        if ok != 1:
            print('--- crawlComments failed...', ok, '\n', flush=True)
            return

        payload = jsonData['data']
        commentDatas = payload['data']

        index = 0
        for commentData in commentDatas:
            index += 1
            if index > self.commentNumber:
                break

            comment = Comment()
            comment.cindex = index
            comment.fromJsonData(commentData)
            post.comments.append(comment)
            #print('--- crawlComments post comment ---', comment, '\n', flush=True)

    def crawlRemarks(self, comment):
        print('--- crawlRemarks comment ---', comment.cid, comment.total_number, self.remarkNumber, '\n', flush=True)

        # if not comment.child:
        #     print('--- crawlRemarks comment no remarks ---', comment.cid, comment.total_number, '\n', flush=True)
        #     return

        url = r'https://m.weibo.cn/comments/hotFlowChild?cid=%s&max_id=0&max_id_type=0' %(comment.cid)
        rsp = requests.get(url, headers = self.headers)

        jsonString = rsp.content.decode('utf-8')
        if jsonString.find('data') == -1:
            print('--- crawlRemarks comment no remarks ---', comment.cid, comment.total_number, '\n', flush=True)
            return

        jsonData = json.loads(jsonString)
        #print('--- crawlRemarks rsp data ---', jsonData, '\n', flush=True)

        ok = jsonData['ok']
        if ok != 1:
            print('--- crawlRemarks failed...', ok, '\n', flush=True)
            return

        payload = jsonData['data']
        remarkDatas = payload

        index = 0
        for remarkData in remarkDatas:
            index += 1
            if index > self.remarkNumber:
                break

            remark = Remark()
            remark.rindex = index
            remark.fromJsonData(remarkData)
            comment.remarks.append(remark)
            #print('--- crawlRemarks comment remark ---', remark, '\n', flush=True)
