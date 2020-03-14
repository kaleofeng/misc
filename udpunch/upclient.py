#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import io
import logging
import socket
import string
import struct
import sys
import threading

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

remoteHost = 'www.metazion.net'
remotePort = 10080
remoteAddr = (remoteHost, remotePort)

cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SELF_ID = 1

friends = {}

CMD_REGISTER = 1001

CMD_SYNC = 2001
CMD_WELCOME = 2002

CMD_HI = 3001

def sayHi(id, peerAddr):
    print('sayHi', id, peerAddr, flush=True)

    msg = struct.pack('ii2s', CMD_HI, id, b'Hi')
    cs.sendto(msg, peerAddr)

def handleSync(data, peerAddr):
    print('handleSync', data, peerAddr, flush=True)

    fields = struct.unpack('i15si', data)
    print('handleSync', fields, flush=True)

    id = fields[0]
    ip = str.rstrip(fields[1].decode('utf-8'), '\0')
    port = fields[2]
    friends[id] = (ip, port)
    print('handleSync', id, ip, len(ip), port, flush=True)

    sayHi(id, (ip, port))

def handleWelcome(data, peerAddr):
    print('handleWelcome', data, peerAddr, flush=True)

    fields = struct.unpack('i7s', data)
    peerId = fields[0]
    info = fields[1]
    print('handleWelcome', peerId, info, peerAddr, flush=True)

def handleHi(data, peerAddr):
    print('handleHi', data, peerAddr, flush=True)

    fields = struct.unpack('i2s', data)
    peerId = fields[0]
    info = fields[1]
    print('handleHi', peerId, info, peerAddr, flush=True)

def handleUnknown(data, peerAddr):
    print('handleUnknown', data, peerAddr, flush=True)

handles = {
    CMD_SYNC: handleSync,
    CMD_WELCOME: handleWelcome,

    CMD_HI: handleHi
}

def processMsg(msg, peerAddr):
    print('processMsg', msg, peerAddr, flush=True)

    cmd = struct.unpack('i', msg[:4])[0]
    data = msg[4:]
    print('processMsg', cmd, data, flush=True)

    handles.get(cmd, handleUnknown)(data, peerAddr)

def register():
    msg = struct.pack('ii', CMD_REGISTER, SELF_ID)
    cs.sendto(msg, remoteAddr)
    print('register', msg, remoteAddr)

def tick():
    try:
        while True:
            msg, peerAddr = cs.recvfrom(1024)
            print(msg, len(msg), peerAddr, flush=True)

            processMsg(msg, peerAddr)
    except socket.error as e:
        print('tick', e, flush=True)
    except KeyboardInterrupt:
        cs.close()

def command():
    while True:
        try:
            id = int(input('Input target id: '))
            print('command', id, friends, flush=True)

            peerAddr = friends.get(id, ())
            sayHi(id, peerAddr)
        except Exception as e:
            print('command', e, flush=True)

def main():
    global SELF_ID
    SELF_ID = int(sys.argv[1])

    register()

    t1 = threading.Thread(target=tick, args=())
    t1.start()

    t2 = threading.Thread(target=command, args=())
    t2.start()

if __name__ == '__main__':
    main()
