#!/usr/bin/env python
#    Modified version of hello.py from python-fuse examples by Andrew Straw
#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os, stat, errno, sys
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse
# sudo apt-get install python-bitsring
# if on your own system CHECK IF ON UNIVERSITY/PI??
import numpy

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

rand_path = '/rand'
bit_path = "/home/scotth3n/Documents/python-fuse-master/example/rand.py"
class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class RandFS(Fuse):

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = os.path.getsize(bit_path)
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', rand_path[1:]:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        # might need to work on this??
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        totalBytes = os.path.getsize(bit_path)
        bytes      = numpy.fromfile(bit_path, dtype="uint8")
        buf = ""
        # TODO check if size of rand file is large enough
        # for request
        if totalBytes > size:
            for by in bytes:
                buf += str(int(by, 2))
                buf += '\n'
        else:
            indx = 0
            bitstr = numpy.unpackbits(bytes)
            for i in range(0, totalBytes)
                bitsub = bitstr[indx:indx+8]
                indx += 8
                buf += str(int(bitstr, 2)) + "\n"
            #generate rand bits
        return buf

def main():
    usage="""
""" + Fuse.fusage
    server = RandFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
