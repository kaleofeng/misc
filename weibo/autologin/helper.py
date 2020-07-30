#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo

def doPost(client, content):
    print('doPost', content, '\n', flush=True)

    client.post(content)
    ret = client.code == 100000
    if not ret:
        print('!!! doPost failed !!!', '\n', flush=True)

    return ret

def doFollow(client, uid):
    print('doFollow', uid, '\n', flush=True)

    client.follow(uid)
    ret = client.code == 100000
    if not ret:
        print('!!! doFollow failed !!!', uid, '\n', flush=True)

    return ret

def doLike(client, rmid):
    print('doLike', rmid, '\n', flush=True)

    client.like(rmid)
    ret = client.code == 100000
    if not ret:
        print('!!! doLike failed !!!', rmid, '\n', flush=True)

    return ret

def doComment(client, rmid, rcs, forward):
    print('doComment', rmid, rcs, '\n', flush=True)

    client.comment(rmid, rcs, forward)
    ret = client.code == 100000
    if not ret:
        print('!!! doComment failed !!!', rmid, '\n', flush=True)

    return ret

def doForward(client, rmid, rfs, comment):
    print('doForward', rmid, rfs, comment, '\n', flush=True)

    client.forward(rmid, rfs, comment)
    ret = client.code == 100000
    if not ret:
        print('!!! doForward failed !!!', rmid, rfs, comment, '\n', flush=True)

    return ret

def doILike(client, rmid, iuid, imid):
    print('doILike', rmid, iuid, imid, '\n', flush=True)

    client.ilike(rmid, iuid, imid)
    ret = client.code == 100000
    if not ret:
        print('!!! doILike failed !!!', rmid, iuid, imid, '\n', flush=True)

    return ret

def doIComment(client, ruid, rmid, iuid, imid, ics):
    print('doIComment', ruid, rmid, iuid, imid, ics, '\n', flush=True)

    client.icomment(ruid, rmid, iuid, imid, ics)
    ret = client.code == 100000
    if not ret:
        print('!!! doIComment failed !!!', ruid, rmid, iuid, imid, '\n', flush=True)

    return ret

def doTFollow(client, tid):
    print('doTFollow', tid, '\n', flush=True)

    client.tfollow(tid)
    ret = client.code == 100000
    if not ret:
        print('!!! doTFollow failed !!!', tid, '\n', flush=True)

    return ret

def doTSignIn(client, tid):
    print('doTSignIn', tid, '\n', flush=True)

    client.tsignin(tid)
    ret = client.code == 100000
    if not ret:
        print('!!! doTSignIn failed !!!', tid, '\n', flush=True)

    return ret

def doTPost(client, tid, content, picture):
    print('doTPost', tid, content, picture, '\n', flush=True)

    client.tpost(tid, content, picture)
    ret = client.code == 100000
    if not ret:
        print('!!! doTPost failed !!!', tid, content, picture, '\n', flush=True)

    return ret

def doTComment(client, tid, mid, content, forward):
    print('doTComment', tid, mid, content, forward, '\n', flush=True)

    client.tcomment(tid, mid, content, forward)
    ret = client.code == 100000
    if not ret:
        print('!!! doTComment failed !!!', tid, mid, content, forward, '\n', flush=True)

    return ret

def doTLao(client, tid, content, number):
    print('doTLao', tid, content, number, '\n', flush=True)

    client.tlao(tid, content, number)
    ret = client.code == 100000
    if not ret:
        print('!!! doTLao failed !!!', tid, content, number, '\n', flush=True)

    return ret
