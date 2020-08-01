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
        tid = ti['tid']
        helper.doTFollow(client, tid)
        helper.doTSignIn(client, tid)
        time.sleep(3)

    tls = tasks.get('tls', [])
    for tl in tls:
        tid = tl['tid']
        content = tl['content']
        number = tl['number']
        helper.doTLao(client, tid, content, number)
        time.sleep(3)

    tps = tasks.get('tps', [])
    for tp in tps:
        tid = tp['tid']
        content = tp['content']
        picture = tp['picture']
        helper.doTPost(client, tid, content, picture)
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
