#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import time
import sys

import util
import weibo

def doPost(client, content):
    print('doPost', content, '\n', flush = True)

    client.post(content)
    ret = client.code == 100000
    if not ret:
        print('!!! doPost failed !!!', '\n', flush = True)

    return ret

def doFollow(client, uid):
    print('doFollow', uid, '\n', flush = True) 

    client.follow(uid)
    ret = client.code == 100000
    if not ret:
        print('!!! doFollow failed !!!', uid, '\n', flush = True)

    return ret

def doLike(client, rmid):
    print('doLike', rmid, '\n', flush = True) 

    client.like(rmid)
    ret = client.code == 100000
    if not ret:
        print('!!! doLike failed !!!', rmid, '\n', flush = True)

    return ret

def doComment(client, rmid, rcs, forward):
    print('doComment', rmid, rcs, '\n', flush = True)

    client.comment(rmid, rcs, forward)
    ret = client.code == 100000
    if not ret:
        print('!!! doComment failed !!!', rmid, '\n', flush = True)

    return ret

def doForward(client, rmid, rfs, comment):
    print('doForward', rmid, rfs, comment, '\n', flush = True)

    client.forward(rmid, rfs, comment)
    ret = client.code == 100000
    if not ret:
        print('!!! doForward failed !!!', rmid, rfs, comment, '\n', flush = True)

    return ret

def doILike(client, rmid, iuid, imid):
    print('doILike', rmid, iuid, imid, '\n', flush = True)

    client.ilike(rmid, iuid, imid)
    ret = client.code == 100000
    if not ret:
        print('!!! doILike failed !!!', rmid, iuid, imid, '\n', flush = True)

    return ret

def doIComment(client, ruid, rmid, iuid, imid, ics):
    print('doIComment', ruid, rmid, iuid, imid, ics, '\n', flush = True)

    client.icomment(ruid, rmid, iuid, imid, ics)
    ret = client.code == 100000
    if not ret:
        print('!!! doIComment failed !!!', ruid, rmid, iuid, imid, '\n', flush = True)

    return ret

def doPatch(tasks, username, password, oddeven):
    print('doPatch begin: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush = True)

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
    ret = doFollow(client, uid)
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
                    ret = doIComment(client, ruid, rmid, iuid, imid, ics)
                    # print('--- ics ---', ics, '\n', flush = True)
                    if not ret:
                        icfWell = False

                if not icfWell:
                    eicfs.append({ 'ruid': ruid, 'rmid': rmid, 'iuid': iuid, 'imid': imid })
                
                # 点赞
                if ilikeWell:
                    time.sleep(2)
                    ret = doILike(client, rmid, iuid, imid)
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
                ret = doForward(client, rmid, rfs, 1)
                # print('--- rfs ---', rfs, '\n', flush = True)
                if not ret:
                    cfWell = False   

            if not cfWell:
                ercfs.append({ 'rmid': rmid })

            # 点赞
            if likeWell:
                time.sleep(2)
                ret = doLike(client, rmid)
                if not ret:
                    likeWell = False
            
            if not likeWell:
                erlikes.append({ 'rmid': rmid })

    # 重做出错部分
    if not ilikeWell or not icfWell or not likeWell or not cfWell:    
        time.sleep(20)
   
    for eilike in eilikes:
        print('+++ redo eilike +++', eilike, '\n', flush = True)
        ret = doILike(client, eilike['rmid'], eilike['iuid'], eilike['imid'])
        if not ret:
            break
        time.sleep(5)

    for eicf in eicfs:
        print('+++ redo eicf +++', eicf, '\n', flush = True)
        ics = random.sample(tasks['ics'], 1)[0] %(util.randomText(9))
        ret = doIComment(client, eicf['ruid'], eicf['rmid'], eicf['iuid'], eicf['imid'], ics)
        if not ret:
            break
        time.sleep(5)
     
    for erlike in erlikes:
        print('+++ redo erlike +++', erlike, '\n', flush = True)
        ret = doLike(client, erlike['rmid'])
        if not ret:
            break
        time.sleep(5)

    for ercf in ercfs:
        print('+++ redo ercf +++', ercf, '\n', flush = True)
        rcs = random.sample(tasks['rcs'], 1)[0] %(util.randomText(9))
        ret = doComment(client, ercf['rmid'], rcs, 1)
        if not ret:
            break
        time.sleep(5)

    client.logout()
    
    print('doPatch end: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '\n', flush = True)
    return True

if __name__ == '__main__':
    oddeven = int(sys.argv[1])

    print('^^^ args ^^^', oddeven, '\n', flush = True)

    cf = open('config.json', 'r', encoding = 'utf-8')
    config = json.load(cf)
    cf.close()

    print('$$$ config $$$', config, '\n', flush = True)

    for account in config['accounts']:
        print("&&& account &&&", account, '\n', flush = True)

        username = account['username']
        password = account['password']

        ret = doPatch(config['tasks'], username, password, oddeven)
        if ret:
            print("*** doPatch %s success, well done ***!" %(oddeven), username, password, '\n', flush = True)
        else:
            print("!!! doPatch %s failed !!!" %(oddeven), username, password, '\n', flush = True)
