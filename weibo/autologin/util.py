#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import binascii
import json
import random
import re
import requests
import rsa
import string
import urllib

def encodeUsername(username):
    return base64.encodestring(username.encode('utf-8'))[:-1]

def encodePassword(password, servertime, nonce, pubkey):
    rsaKey = int(pubkey, 16)
    rsaPubKey = rsa.PublicKey(rsaKey, 65537)
    codeString = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    pwd = rsa.encrypt(codeString.encode('utf-8'), rsaPubKey)
    return binascii.b2a_hex(pwd)

def encodePostData(username, password, servertime, nonce, pubkey, rsakv):
    su = encodeUsername(username)
    sp = encodePassword(password, servertime, nonce, pubkey)

    postData = {
        "cdult": "3",
        "domain": "sina.com.cn",
        "encoding": "UTF-8",
        "entry": "account",
        "from": "",
        "gateway": "1",
        "nonce": nonce,
        "pagerefer": "http://login.sina.com.cn/sso/logout.php",
        "prelt": "41",
        "pwencode": "rsa2",
        "returntype": "TEXT",
        "rsakv": rsakv,
        "savestate": "30",
        "servertime": servertime,
        "service": "sso",
        "sp": sp,
        "sr": "1366*768",
        "su": su,
        "useticket": "0",
        "vsnf": "1"
    }
    return postData

def randomText(length):
    text = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return text

def responseCode(text):
    codes = re.findall('code":"(\d*?)"', text)
    if len(codes) > 0:
        return int(codes[0])
    codes = re.findall('code":(\d*?)[,}]', text)
    if len(codes) > 0:
        return int(codes[0])
    return -1
