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

localHost = '0.0.0.0'
localPort = 10080

ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ss.bind((localHost, localPort))

clients = {}

CMD_REGISTER = 1001

CMD_SYNC = 2001

def syncOtherClient(id, addr, peerAddr):
    print('syncOtherClient', id, addr, peerAddr, flush=True)

    data = struct.pack('i15si', id, addr[0].encode('utf-8'), addr[1])
    print('syncOtherClient', data, flush=True)

    msgFmt = 'i{}s'.format(len(data))
    msg = struct.pack(msgFmt, CMD_SYNC, data)
    print('syncOtherClient', msg, flush=True)

    ss.sendto(msg, peerAddr)

def handleRegister(data, peerAddr):
    print('handleRegister', data, peerAddr, flush=True)

    fields = struct.unpack('i', data)
    id = fields[0]
    clients[id] = peerAddr
    print('handleRegister', clients, flush=True)

    for (k, v) in clients.items():
        print(k, v, flush=True)
        if k != id:
            syncOtherClient(id, peerAddr, v)
            syncOtherClient(k, v, peerAddr)

def handleUnknown(data, peerAddr):
    print('handleUnknown', data, peerAddr, flush=True)

handles = {
    CMD_REGISTER: handleRegister,
}

def handleMsg(msg, peerAddr):
    print('handleMsg', msg, peerAddr, flush=True)

    cmd = struct.unpack('i', msg[:4])[0]
    data = msg[4:]
    print('handleMsg', cmd, data, flush=True)

    handles.get(cmd, handleUnknown)(data, peerAddr)

def main():
    try:
        while True:
            msg, peerAddr = ss.recvfrom(1024)
            print(msg, len(msg), peerAddr, flush=True)

            handleMsg(msg, peerAddr)
    except socket.error as e:
        print(e, flush=True)
    except KeyboardInterrupt:
        ss.close()

if __name__ == '__main__':
    main()
