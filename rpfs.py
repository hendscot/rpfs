#!/usr/bin/env python
#    Modified version of hello.py from python-fuse examples by Andrew Straw
#    Modified and Tested by Allo Aymard Assa, Michal Meeker, 
#                           Nathan Poole, Alfred Aboli and
#                           Scott Henderson
#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#
#    RandFS is a specialized file system that does not support creating new files/directories 
#    it simply supports opening a pre-defined file, rand, which returns pseudorandom numbers
#    based on bit input from a file of pseudorandom bits produced by a geiger counter
#    connected to a RaspberryPi
#
import os, stat, errno, sys
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse
import numpy
import random
import time
if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

INT_SIZE = 32
FILE_SIZE = 100
RAND_PATH = '/rand'
BIT_PATH = "/home/scotth3n/Documents/python-fuse-master/example/file.txt"

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
        elif path == RAND_PATH:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = FILE_SIZE
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', RAND_PATH[1:]:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        if path != BIT_PATH:
            return path
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset, fh):
        # We only support reading our "rand" file
        if path == RAND_PATH:
            # totalBytes tracks how many bytes returning
            totalBytes = 0
            # load rand bits file into an ndarray of bytes
            bytes      = numpy.fromfile(BIT_PATH, dtype="uint8")
            # this will be returned, basically a string of all rand ints
            randIntBuf = ""
            # string of "1"s and "0"s stores conversion from ndarray of bits
            bitstring  = ""
            # how many bytes did we use from the file
            bytesUsed  = 0
            # store an ndarray of bits from bytes
            bits = numpy.unpackbits(bytes)
            # do have enough bits for at least one 32-bit int
            if bits.size >= INT_SIZE:
                # while we have enough bits for at least one 32-bit int
                while bits.size >= INT_SIZE:
                    # convert first 32 bits to a regular python string
                    bitstring = self.bitstostring(bits[:INT_SIZE])
                    # convert that string of bits to an integer, and then to a string
                    # then that gets appended to our return buf (with a newline char)
                    randIntBuf += str(int(bitstring, 2)) + '\n'
                    # dispose of those bits
                    bits = bits[INT_SIZE:]
                    # we used 32 bits so 4 bytes
                    bytesUsed += 4
                # our total byte amount is equal to the length of our buffer
                totalBytes += len(randIntBuf)
                # dispose of the bytes used
                bytes = bytes[bytesUsed:]
                # now write remaining bytes to the rand bits file
                # this isn't ideal, as we currently are reading 
                # the entire file regardless of request
                bytes.tofile(BIT_PATH)
            # seed with time
            random.seed(time.time())
            # generate more numbers until we reach our
            # arbitrary max size
            # this could overflow if totalBytes + 5 > FILE_SIZE
            # but shouldn't cause any problems
            while totalBytes < FILE_SIZE:
                bitstring = ""
                # we want 32 bits
                for i in range (0, 32):
                    # generate a float between 0 and 1
                    # if over .5, we want a 1
                    if random.uniform(0, 1) > .5:
                        bitstring += "1"
                    # less than or = to .5 we want a 0
                    else:
                        bitstring += "0"
                # append new number and newline to return buffer
                randIntBuf += str(int(bitstring, 2)) + "\n"
                # update totalBytes size
                totalBytes = len(randIntBuf)
            #now we can return buffer
            return randIntBuf
        # reading any file but our random bits is not supported!
        else:
            return -errno.ENOENT
    # helper function which converts an ndarray of bits to string of bits
    def bitstostring(self, bits):
        sbuf = ""
        for bit in bits:
            sbuf += str(bit)
        return sbuf
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
