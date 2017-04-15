#!/usr/bin/env python

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com> "Hello.py"
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#
#    This file uses `python-fuse`, github.com/libfuse/python-fuse
#       See also "xmp.py" for another example
#
#    Modified By: Nathan M. Poole, A3-FUSE group project C435

import os, stat, errno
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

hello_path = '/hello'         #simulated file name
hello_str = 'Hello World!\n'  #simulated file content

#Adding two new files names
gRand_path = '/g_rand'
gCPM_path = '/g_cpm'

#A new size value for the files
MAX_DIGITS = 10 #10 digits (32bit Int)

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

class HelloFS(Fuse):

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        elif path == hello_path:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = len(hello_str)
        elif path == gRand_path:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = MAX_DIGITS
        elif path == gCPM_path:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = MAX_DIGITS
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', hello_path[1:], gRand_path[1:], gCPM_path[1:]:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        if path != hello_path and path != gRand_path and path != gCPM_path:
            return -errno.ENOENT
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        if path == hello_path
            slen = len(hello_str)
            if offset < slen:
                if offset + size > slen:
                    size = slen - offset
                buf = hello_str[offset:offset+size]
            else:
                buf = ''
        elif path == gRand_path or path == gCPM_path:
            #All we need to do is return the number of digits
            #that are requested by "size" attribute, ignore offset
            #or the current CPM value
        else:
            return -errno.ENOENT
        return buf

def main():
    usage="""
Userspace hello example
""" + Fuse.fusage
    server = HelloFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
  main()
