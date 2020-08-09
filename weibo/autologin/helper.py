#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo

def doPost(client, text):
    print('Do Post', text, '\n', flush=True)

    client.post(text)
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

def doHFollow(client, hid):
    print('DO H Follow', hid, '\n', flush=True)

    client.hfollow(hid)
    ret = client.code == 100000
    if not ret:
        print('DO H Follow failed!', hid, '\n', flush=True)

    return ret

def doHSignIn(client, hid):
    print('DO H SignIn', hid, '\n', flush=True)

    client.hsignin(hid)
    ret = client.code == 100000
    if not ret:
        print('DO H SignIn failed!', hid, '\n', flush=True)

    return ret

def doHPost(client, hid, text, picture):
    print('DO H Post', hid, text, picture, '\n', flush=True)

    client.hpost(hid, text, picture)
    ret = client.code == 100000
    if not ret:
        print('DO H Post failed!', hid, text, picture, '\n', flush=True)

    return ret

def doHComment(client, hid, mid, text, forward):
    print('DO H Comment', hid, mid, text, forward, '\n', flush=True)

    client.hcomment(hid, mid, text, forward)
    ret = client.code == 100000
    if not ret:
        print('DO H Comment failed!', hid, mid, text, forward, '\n', flush=True)

    return ret

def doHSalvage(client, hid, text, number, commentThreshold):
    print('DO H Salvage', hid, text, number, commentThreshold, '\n', flush=True)

    client.hsalvage(hid, text, number, commentThreshold)
    ret = client.code == 100000
    if not ret:
        print('DO H Salvage failed!', hid, text, number, commentThreshold, '\n', flush=True)

    return ret
