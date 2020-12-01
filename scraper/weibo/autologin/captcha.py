#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import json
import os
import PIL.Image as Image
import re
import requests
import sys
import time
import webbrowser

def identifyLocal(captchaUrl):
    print('Captcha - Identify Local', captchaUrl, '\n', flush=True)

    rsp = requests.get(captchaUrl)

    # Show in local image
    bio = io.BytesIO()
    bio.write(rsp.content)
    img = Image.open(bio)
    img.show()

    # Show in web browser
    # webbrowser.open_new_tab(captchaUrl)

    captchaText = input('Input captcha of url above: ')
    return captchaText

def identifyRemote(captchaUrl):
    print('Captcha - Identify Remote', captchaUrl, '\n', flush=True)

    applyReceiver = '01d7dd1057d740eda6471100af0d0be0'

    url = r'https://apply.metazion.net/applies/apply'
    reqData = {
        'id': '10001',
        'sender': '微博自动登录程序',
        'receiver': applyReceiver,
        'content': '请识别验证码并回复|验证码图片{#i:%s}' % (captchaUrl)
    }
    headers = {
        'Content-Type': 'application/json'
    }
    rsp = requests.post(url, data=json.dumps(reqData), headers=headers)

    # print('Captcha - Identify Remote: apply url', url, '\n', flush=True)
    # print('Captcha - Identify Remote: apply rsp text', rsp.text, '\n', flush=True)

    rspData = json.loads(rsp.content)
    applySeq = rspData['data']

    while True:
        print('Captcha - Identify Remote: waiting remote identification response...', '\n', flush=True)

        url = r'https://apply.metazion.net/applies/query?whom=%s&seq=%s' % (applyReceiver, applySeq)
        rsp = requests.get(url)

        # print('Captcha - Identify Remote: query url', url, '\n', flush=True)
        # print('Captcha - Identify Remote: query rsp status code', rsp.status_code, '\n', flush=True)

        if rsp.status_code != 200:
            print('Captcha - Identify Remote: waiting remote timeout, try again!', '\n', flush=True)
            continue

        rspData = json.loads(rsp.content)
        captchaText = rspData['data']
        return captchaText
