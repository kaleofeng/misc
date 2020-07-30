#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo
import helper

def doBatch(tasks, username, password, oddeven):
    print('doBatch begin: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush=True)

    client = weibo.Weibo()
    client.login(username, password)
    if not client.state:
        client.logout()
        return False

    eicfs = []
    eilikes = []

    ercfs = []
    erlikes = []

    uid = tasks.get('uid', 5644764907)

    icfWell = True
    ilikeWell = True
    cfWell = True
    likeWell = True

    time.sleep(2)

    # 先关注，然后全部赞评转
    ret = helper.doFollow(client, uid)
    if ret:
        # 根微博
        rms = tasks.get('rms', [])
        for rm in rms:
            ruid = rm.get('ruid', uid)
            rmid = rm['rmid']

            # 奇偶分批
            if rmid % 2 == oddeven:
                continue

            time.sleep(6)

            # 子微博
            ims = rm.get('ims', [])
            for im in ims:
                iuid = im.get('iuid', uid)
                imid = im['imid']

                # 只关注目标用户
                if iuid != uid:
                    continue

                # 评论
                if icfWell:
                    time.sleep(2)
                    ics = random.sample(tasks['ics'], 1)[0] %(util.randomText(9))
                    ret = helper.doIComment(client, ruid, rmid, iuid, imid, ics)
                    # print('--- ics ---', ics, '\n', flush=True)
                    if not ret:
                        icfWell = False

                if not icfWell:
                    eicfs.append({ 'ruid': ruid, 'rmid': rmid, 'iuid': iuid, 'imid': imid })

                # 点赞
                if ilikeWell:
                    time.sleep(2)
                    ret = helper.doILike(client, rmid, iuid, imid)
                    if not ret:
                        ilikeWell = False

                if not ilikeWell:
                    eilikes.append({ 'rmid': rmid, 'iuid': iuid, 'imid': imid })

            # 只关注目标用户
            if ruid != uid:
                continue

            # 转发带评论或评论带转发模式切换
            if cfWell:
                time.sleep(2)
                rfs = random.sample(tasks['rfs'], 1)[0] %(util.randomText(9))
                ret = helper.doForward(client, rmid, rfs, 1)
                # print('--- rfs ---', rfs, '\n', flush=True)
                if not ret:
                    cfWell = False

            if not cfWell:
                ercfs.append({ 'rmid': rmid })

            # 点赞
            if likeWell:
                time.sleep(2)
                ret = helper.doLike(client, rmid)
                if not ret:
                    likeWell = False

            if not likeWell:
                erlikes.append({ 'rmid': rmid })

    # 重做出错部分
    if not ilikeWell or not icfWell or not likeWell or not cfWell:
        time.sleep(20)

    for eilike in eilikes:
        print('+++ redo eilike +++', eilike, '\n', flush=True)
        ret = helper.doILike(client, eilike['rmid'], eilike['iuid'], eilike['imid'])
        if not ret:
            break
        time.sleep(5)

    for eicf in eicfs:
        print('+++ redo eicf +++', eicf, '\n', flush=True)
        ics = random.sample(tasks['ics'], 1)[0] %(util.randomText(9))
        ret = helper.doIComment(client, eicf['ruid'], eicf['rmid'], eicf['iuid'], eicf['imid'], ics)
        if not ret:
            break
        time.sleep(5)

    for erlike in erlikes:
        print('+++ redo erlike +++', erlike, '\n', flush=True)
        ret = helper.doLike(client, erlike['rmid'])
        if not ret:
            break
        time.sleep(5)

    for ercf in ercfs:
        print('+++ redo ercf +++', ercf, '\n', flush=True)
        rcs = random.sample(tasks['rcs'], 1)[0] %(util.randomText(9))
        ret = helper.doComment(client, ercf['rmid'], rcs, 1)
        if not ret:
            break
        time.sleep(5)

    client.logout()

    print('doBatch end: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush=True)
    return True

if __name__ == '__main__':
    oddeven = int(sys.argv[1])

    print('^^^ args ^^^', oddeven, '\n', flush=True)

    cf = open('data/batch.json', 'r', encoding = 'utf-8')
    config = json.load(cf)
    cf.close()

    print('$$$ config $$$', config, '\n', flush=True)

    for account in config['accounts']:
        print("&&& account &&&", account, '\n', flush=True)

        username = account['username']
        password = account['password']

        ret = doBatch(config['tasks'], username, password, oddeven)
        if ret:
            print("*** doBatch %s success, well done ***!" %(oddeven), username, password, '\n', flush=True)
        else:
            print("!!! doBatch %s failed !!!" %(oddeven), username, password, '\n', flush=True)
