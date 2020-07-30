#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo
import helper

def doBatch(tasks, username, password):
    print('doBatch begin: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush = True)

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

    tps = tasks.get('tps', [])
    for tp in tps:
        tid = tp['tid']
        content = tp['content']
        picture = tp['picture']
        helper.doTPost(client, tid, content, picture)
        time.sleep(3)

    print('doBatch end: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush = True)
    return True

if __name__ == '__main__':
    cf = open('data/topic.json', 'r', encoding = 'utf-8')
    config = json.load(cf)
    cf.close()

    print('$$$ config $$$', config, '\n', flush = True)

    for account in config['accounts']:
        print("&&& account &&&", account, '\n', flush = True)

        username = account['username']
        password = account['password']

        ret = doBatch(config['tasks'], username, password)
        if ret:
            print("*** doBatch success, well done ***!", username, password, '\n', flush = True)
        else:
            print("!!! doBatch failed !!!", username, password, '\n', flush = True)
