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

class GFS(Fuse):

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
        elif path == gRand_path:
            #Ignore offset
            #Size = num of rand numbers requested
            #Path = the name of the file to access(gRand)
            #buf = return variable to be filled with data

            #ALG:
              #1. Get the data from the randbits.txt file
              #2. Sort data into array of each line as one element
              #3. Based on "size" determine if enough elements are available for request(sizex9){9C2}
              #4. If not enough elements, attempt to generate more, jmp #?
              #5. If enough elements, use combination math and comparisons to generate 32bits x size
              #6. Pack each 32bit set into a number and add number as an element to the return variable
              #   jmp, #11
              #7. Determine amount of elements to generate based on current element count and "size"
              #8. Repeat Until requirements met: Use each element + timestamp to gen. new rand num.
              #9. After first run, use new rand numbers + timestamp to gen new rand numbers.
              #10. Once finished, jmp #5.
              #11. Finally clear all used elements from the randbits file

        elif path == gCPM_path:
            #Ignore offset
            #Ignore size, size = w/e size the number is
            #Path = the name of the file to access(gCPM)
            #buf = return variable to be filled with data
        else:
            return -errno.ENOENT
        return buf

def main():
    usage="""
GFS - Geiger File System\n
\n
This file system is designed to simulate a file based access\n
method to retrieve random bits/numbers from geiger counter hardware.
""" + Fuse.fusage
    server = GFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
  main()
