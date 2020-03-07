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

CMD_REGISTER = 1001

CMD_SYNC = 2001

CMD_HI = 3001

def handleSync(data, peerAddr):
    print('handleSync', data, peerAddr, flush=True)

    fields = struct.unpack('i15si', data)
    print('handleSync', fields, flush=True)

    id = fields[0]
    ip = str.rstrip(fields[1].decode('utf-8'), '\0')
    port = fields[2]
    print('handleSync', id, ip, len(ip), port, flush=True)

    msg = struct.pack('ii2s', CMD_HI, SELF_ID, b'Hi')
    cs.sendto(msg, (ip, port))
    cs.sendto(msg, (ip, port))

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

    CMD_HI: handleHi
}

def handleMsg(msg, peerAddr):
    print('handleMsg', msg, peerAddr, flush=True)

    cmd = struct.unpack('i', msg[:4])[0]
    data = msg[4:]
    print('handleMsg', cmd, data, flush=True)

    handles.get(cmd, handleUnknown)(data, peerAddr)

def register():
    msg = struct.pack('ii', CMD_REGISTER, SELF_ID)
    cs.sendto(msg, remoteAddr)
    print(msg, remoteAddr)

def main():
    global SELF_ID
    SELF_ID = int(sys.argv[1])

    register()

    try:
        while True:
            msg, peerAddr = cs.recvfrom(1024)
            print(msg, len(msg), peerAddr, flush=True)

            handleMsg(msg, peerAddr)
    except socket.error as e:
        print(e, flush=True)
    except KeyboardInterrupt:
        cs.close()

if __name__ == '__main__':
    main()
