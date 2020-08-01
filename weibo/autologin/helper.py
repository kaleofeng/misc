#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo

def doPost(client, content):
    print('Do Post', content, '\n', flush=True)

    client.post(content)
    ret = client.code == 100000
    if not ret:
        print('Do Post failed!', '\n', flush=True)

    return ret

def doFollow(client, uid):
    print('Do Follow', uid, '\n', flush=True)

    client.follow(uid)
    ret = client.code == 100000
    if not ret:
        print('Do Follow failed!', uid, '\n', flush=True)

    return ret

def doLike(client, rmid):
    print('Do Like', rmid, '\n', flush=True)

    client.like(rmid)
    ret = client.code == 100000
    if not ret:
        print('Do Like failed!', rmid, '\n', flush=True)

    return ret

def doComment(client, rmid, rcs, forward):
    print('Do Comment', rmid, rcs, '\n', flush=True)

    client.comment(rmid, rcs, forward)
    ret = client.code == 100000
    if not ret:
        print('Do Comment failed!', rmid, '\n', flush=True)

    return ret

def doForward(client, rmid, rfs, comment):
    print('Do Forward', rmid, rfs, comment, '\n', flush=True)

    client.forward(rmid, rfs, comment)
    ret = client.code == 100000
    if not ret:
        print('Do Forward failed!', rmid, rfs, comment, '\n', flush=True)

    return ret

def doILike(client, rmid, iuid, imid):
    print('Do I Like', rmid, iuid, imid, '\n', flush=True)

    client.ilike(rmid, iuid, imid)
    ret = client.code == 100000
    if not ret:
        print('Do I Like failed!', rmid, iuid, imid, '\n', flush=True)

    return ret

def doIComment(client, ruid, rmid, iuid, imid, ics):
    print('Do I Comment', ruid, rmid, iuid, imid, ics, '\n', flush=True)

    client.icomment(ruid, rmid, iuid, imid, ics)
    ret = client.code == 100000
    if not ret:
        print('Do I Comment failed!', ruid, rmid, iuid, imid, '\n', flush=True)

    return ret

def doTFollow(client, tid):
    print('Do T Follow', tid, '\n', flush=True)

    client.tfollow(tid)
    ret = client.code == 100000
    if not ret:
        print('Do T Follow failed!', tid, '\n', flush=True)

    return ret

def doTSignIn(client, tid):
    print('Do T SignIn', tid, '\n', flush=True)

    client.tsignin(tid)
    ret = client.code == 100000
    if not ret:
        print('Do T SignIn failed!', tid, '\n', flush=True)

    return ret

def doTPost(client, tid, content, picture):
    print('Do T Post', tid, content, picture, '\n', flush=True)

    client.tpost(tid, content, picture)
    ret = client.code == 100000
    if not ret:
        print('Do T Post failed!', tid, content, picture, '\n', flush=True)

    return ret

def doTComment(client, tid, mid, content, forward):
    print('Do T Comment', tid, mid, content, forward, '\n', flush=True)

    client.tcomment(tid, mid, content, forward)
    ret = client.code == 100000
    if not ret:
        print('Do T Comment failed!', tid, mid, content, forward, '\n', flush=True)

    return ret

def doTLao(client, tid, content, number):
    print('Do T Lao', tid, content, number, '\n', flush=True)

    client.tlao(tid, content, number)
    ret = client.code == 100000
    if not ret:
        print('Do T Lao failed!', tid, content, number, '\n', flush=True)

    return ret
