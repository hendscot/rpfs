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

import os, stat, errno, random, time
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

#Full path to the random bits file
BIT_PATH = "/home/nmpoole/fuse/randtimegeiger.txt"

#A new size value for the files
FILE_SIZE = 12

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
    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        #For some reason the read function
        #is ran multiple times for a single read
        #We need buf to be a class variable so 
        #that it doesn't get overwritten on those
        #extra calls after we edit the bits file.
        self.randNum = ''
        self.run = 0
        #If we don't do this, the buf value is crushed
        #and we waste elements and/or crush the bits file.
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
            st.st_size = FILE_SIZE
        elif path == gCPM_path:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = FILE_SIZE
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', hello_path[1:], gRand_path[1:], gCPM_path[1:]:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        
        if path != gRand_path and path != hello_path and path != gCPM_path:
            return -errno.ENOENT
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        if path == hello_path:
            print size, "\n"
            slen = len(hello_str)
            if offset < slen:
                if offset + size > slen:
                    size = slen - offset
                buf = hello_str[offset:offset+size]
            else:
                buf = ''
        elif path == gRand_path:
            #Ignore offset
            #Size = num of bytes/characters to read (this seems to always be 4096, idky)
            #Path = the name of the file to access(gRand)
            #buf = return variable to be filled with data
            if(self.randNum != ''):
              slen = len(self.randNum)
              if(offset < slen):
                if(offset + size > slen):
                  size = slen - offset
                buf = self.randNum[offset:offset+size]
              else:
                buf = ''
            else:
              #Check for randfile availability
              if(os.path.isfile(BIT_PATH) == 0):
                #No File!
                buf = 0
              else:
                #Open up the randFile for reading
                fo = open(BIT_PATH, "r")
                if(fo.closed == "false"):
                  print "Unable to open file ", fo.name, "\n"
                else:
                  print fo.name, " has been successfully opened!\n"
                  
                  #Read the file line by line
                  elist = [] #empty list
                  tmp = fo.readline() #read first line
                  if(tmp == ""): #skip rand generation, file empty
                    self.randNum = 0
                  else:
                    while(tmp != ""):
                      tmp = tmp[:-1] #get rid of '/n'
                      tmp = tmp if (tmp[-3] == ".") else (tmp + "0")#pad decimal 0
                      elist.append(tmp)#add to list and remove
                      tmp = fo.readline()   #read next line from bits file              
                    fo.close()#close the file

                    #Make sure we have enough elements to generate
                    #a single random number: 9C2...
                    tmpList = elist[:] #copy the list so we don't lose it
                    while(len(elist) < 9):
                      random.seed(tmpList.pop(0))#remove first element, set as rand seed
                      elist.append(str(random.random() + time.time()))#append new random number
                    #end Generation loop

                    #Save remaining elements?
                    wlist = elist[9:] if (len(elist) > 9) else []
                    elist = elist[:9]#We have enough elements..take first 9
                    print elist, "\n"
                    randNum = '' #empty string
                    while(len(elist) > 1):#loop until only 1 element left
                      compare = elist.pop(0) #remove/set first element as compare
                      for element in elist: #loop remaining elements
                        if(int(element[-2:]) > int(compare[-2:])):
                          randNum += '0'
                        else:
                          randNum += '1'
                      #list iteration finished
                    print randNum, "\n"
                    print "Count: ", len(randNum), "\n"
                    #end binary loop
                    
                    #convert "binary" string to unsigned int
                    self.randNum = str(int(randNum[:-4], 2)) + "\n"
                    #we also convert back to string so we can return it
                    print "RandNum = ", self.randNum, "\n"
                    #Run offset calculations and come up
                    #With the return variable 'buf' 
                    slen = len(self.randNum)
                    if(offset < slen):
                      if(offset + size > slen):
                       size = slen - offset
                      buf = self.randNum[offset:offset+size]
                    else:
                      buf = ''                    

                    #Rewrite bits file to clear used elements
                    fo = open(BIT_PATH, "w+")
                    if(len(wlist) != 0):
                      for line in wlist:
                        fo.write(line + "\n")
                    else:
                      fo.write('') #Empty File rather than delete it
                    fo.close()
                  #End RandNum generation

        elif path == gCPM_path:
            print "Skipping gCPM"
            #Ignore offset
            #Ignore size, size = w/e size the number is
            #Path = the name of the file to access(gCPM)
            #buf = return variable to be filled with data

            #ALG:
            #1. Get the data from the randbits.txt file
            #2. Sort data into array of each line as one element
            #3. Use first element as start of minute(elements are timestamps)
            #4. Figure out which element is closest to 1min + first element
            #5. Count num of elements between these two. Return count.
            elems = []
            count = 0
            with open("BIT_FILE", "r") as bitfile:
                for line in bitfile:
                    elems.append(line[:-1])
            return ""
        else:
            return -errno.ENOENT

        #Check to see if we are returning self.randNum
        if(buf == self.randNum):
          #We are about to return the whole randNum we made
          #This is the time to clear it for next run
          if(self.run == 0):
            self.run = 1
          else:
            self.run = 0
            self.randNum = ''
          
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
