#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import json
import random
import re
import sys
import time

import util
import weibo
import helper

def doBatch(tasks, username, password):
    client = weibo.Weibo()
    client.login(username, password)
    if not client.state:
        client.logout()
        return False

    tis = tasks.get('tis', [])
    for ti in tis:
        hid = ti['hid']
        helper.doHFollow(client, hid)
        helper.doHSignIn(client, hid)
        time.sleep(3)

    tls = tasks.get('tls', [])
    for tl in tls:
        hid = tl['hid']
        text = tl['text']
        number = tl['number']
        commentThreshold = tl['commentThreshold']
        helper.doHSalvage(client, hid, text, number, commentThreshold)
        time.sleep(3)

    tps = tasks.get('tps', [])
    for tp in tps:
        hid = tp['hid']
        text = tp['text']
        picture = tp['picture']
        helper.doHPost(client, hid, text, picture)
        time.sleep(3)

    return True

if __name__ == '__main__':
    config = []
    with open('data/topic.json', 'r', encoding = 'utf-8') as cf:
      config = json.load(cf)

    print('Config: ', config, '\n', flush=True)

    for account in config['accounts']:
        print("Account: ", account, '\n', flush=True)

        username = account['username']
        password = account['password']

        print('Do Batch begin...', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush=True)

        ret = doBatch(config['tasks'], username, password)

        print('Do Batch end, result[%s]' %(ret), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush=True)
