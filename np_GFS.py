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

import os, stat, errno, random, time, numpy
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
GRAND_PATH = '/g_rand'
GCPM_PATH = '/g_cpm'

#Full path to the random bits file
BIT_PATH = "/home/nmpoole/fuse/randtimegeiger.txt"

#Number of combination elements
#Needed based on byte size requested
BIT_64 = 12 #64 bit uint
BIT_32 = 9  #32 bit uint
BIT_16 = 7  #16 bit uint
BIT_8  = 5  #8  bit uint

SUB_64 = 2 #12C2 = 66(-2) = 64
SUB_32 = 4 #9C2  = 36(-4) = 32
SUB_16 = 5 #7C2  = 21(-5) = 16
SUB_8 = 2  #5C2  = 10(-2) = 8

#A new size value for the files
#(Max number of bytes to return!)
FILE_SIZE = 100

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

    #Initialize GFS class
    def __init__(self, *args, **kw):
        
        #Initialize Fuse parent class
        Fuse.__init__(self, *args, **kw)
        
        #Class variable to hold onto random num
        #we generate for g_rand file
        self.randBytes = ''
        
        #Class variable to track how many times
        #the read function is invoked/run
        self.run = 0
        #If we don't do this, the buf value is crushed
        #and we waste elements generating extra randNums
 
    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        elif path == hello_path:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = len(hello_str)
        elif path == GRAND_PATH:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = 16
        elif path == GCPM_PATH:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = FILE_SIZE
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', hello_path[1:], GRAND_PATH[1:], GCPM_PATH[1:]:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        
        if path != GRAND_PATH and path != hello_path and path != GCPM_PATH:
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
        elif path == GRAND_PATH:
#New ALG:
#Read bits file into 1 line per element array
#Determine if we have enough elements for bytes requested
  #5 elements per byte (5C2 = 10bits-2 = 8bits)
  #If not, generate enough elements for byte request 5*size
#For every "byte" requested:
  #generate an 8 bit binary array ...ex:[1, 1, 0, 0, 0, 1, 1, 0]
  #Remove used elements
#Pack 8bit arrays into numpy.packbits
#Each element of numpy.packbits is now 1 byte of data...
#for each byte of data(element):
  #convert byte to unsigned? char
  #add char to return string
#Run offset calculations on return string
#EoA

            #offset = read offset from first byte
            #size = num of bytes/characters to read (this seems to always be 4096, idky)
            #path = the name of the file to access(gRand)
            #buf = return variable to be filled with data
            if(self.randBytes != ''):
              slen = len(self.randBytes)
              if(offset < slen):
                if(offset + size > slen):
                  size = slen - offset
                buf = self.randBytes[offset:offset+size] + "\n"
              else:
                buf = ''
            else:
              #Check for randfile availability
              if(os.path.isfile(BIT_PATH) == 0):
                #No File!
                buf = 'Sorry, comeback later!'
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
                    self.randBytes = ''
                    buf = ''
                  else:
                    while(tmp != ""):
                      tmp = tmp[:-1] #get rid of '/n'
                      tmp = tmp if (tmp[-3] == ".") else (tmp + "0")#pad decimal 0
                      elist.append(tmp)#add to list
                      tmp = fo.readline()   #read next line from bits file              
                    fo.close()#close the file
                    #elist - now holds each line from the file
                    print "randtimegeiger.txt has ", len(elist), "elements total\n"

                    #Determine how many elements we should use
                    if(size < 2):
                      eNum = BIT_8
                      eSub = SUB_8
                    elif(size < 3):
                      eNum = BIT_16
                      eSub = SUB_16
                    elif(size < 5):
                      eNum = BIT_32
                      eSub = SUB_32
                    else:
                      eNum = BIT_64 #this is the maximum per read
                      eSub = SUB_64

                    #Determine how many elements we should use
                    #size = number of bytes requested, we need
                    #8 bits per size or.. 8bits*size, in order
                    #to generate 8 bits we need 5 elements so 5*size
                    #if we don't have 5*size elements... then just
                    #use all that we do have...? or make enough?
                    #eNum = (5*size)#5Elements per 1byte requested
                    #eNum neeeeds a CAP, 5x4096 = 20480
                    #20480C2 = 209,704,960 (too many!! takes like an hour)
                    #I believe a cap of 8bytes(64bits) is acceptable
                    print "eNum = ", eNum, "\n"

                    #copy the list so we don't lose it
                    tmpList = elist[:]
                    print "tmpList has ", len(tmpList), " elements\n"

                    #Make sure we have eNum elements to use
                    newbies = len(tmpList)#offset to new elements
                    nRun = 1 #current run of newbies
                    while(len(elist) < eNum):
                      #overun check
                      if(tmpList == []):
                        tmpList = elist[(newbies*nRun):]#switch to new numbers generated
                        nRun += 1
                      #end overun check
                      random.seed(tmpList.pop(0))#remove first element, set as rand seed
                      tmp = str(random.random() + time.time()) #create new rand num
                      tmp = tmp if (tmp[-3] == ".") else (tmp + "0")#pad decimal 0
                      elist.append(tmp)#append new random number
                    #end Generation loop

                    #Save remaining elements?
                    wlist = elist[eNum:] if (len(elist) > eNum) else []
                    elist = elist[:eNum]#We have enough elements..take first eNum
                    print "elist has ", len(elist), "elements\n"
                    #elist now holds 5*size elements, no more, no less

                    #Generate a 1 or 0, by comparing each 
                    #element to each other element [(5*size)C2]
                    randBits = [] #empty list
                    while(len(elist) > 1):#loop until only 1 element left
                      compare = elist.pop(0) #remove/set first element as compare
                      print "Compare: ", compare[-2:], "\n"
                      print "elist has ", len(elist), "elements\n"

                      for element in elist: #loop remaining elements
                        if(int(element[-2:]) > int(compare[-2:])):
                          randBits.append(0)
                        else:
                          randBits.append(1)
                      #list iteration finished
                    print randBits, "\n"
                    print "randBits Count: ", len(randBits), "\n"
                    #end binary loop
                    #randBits "list" now holds (eNumC2) 0's and 1's
                    
                    #Seperate into 8bit(element) arrays
                    bitLists = [] #empty list
                    tmpList = [] #empty list
                    for bit in randBits:
                      tmpList.append(bit)
                      if(len(tmpList) == 8):
                        bitLists.append(tmpList)
                        tmpList = []#reset tmpList
                    #bitLists now holds multiple lists of 8 {0s or 1s}
                    print bitLists, "\n"

                    #Convert each 8bit list into string, cast to int, then character
                    #and add it to the self.randBytes string
                    for bitList in bitLists:
                      self.randBytes += chr(int(''.join(str(e) for e in bitList), 2))

                    #numpy convert to array
                    #np = numpy.array(bitLists)
                    #print np, "\n"
                    print self.randBytes, "\n"
                    #seems to work till this point

                    #numpy convert to bytes
                    #self.randBytes = numpy.packbits(np, 1)
                    #print self.randBytes, "\n"
                    #self.randBytes, should now hold multiple elements
                    #each element being an unsigned 8bit integer

                    #Run offset calculations and come up
                    #With the return variable 'buf' 
                    slen = len(self.randBytes)
                    if(offset < slen):
                      if(offset + size > slen):
                       size = slen - offset
                      buf = self.randBytes[offset:offset+size] + "\n"
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

        elif path == GCPM_PATH:
            print "Skipping gCPM"
            #offset = offset from first byte read
            #size = w/e size the number is
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

        #Check to see if we are returning self.randBytes
        if(buf == self.randBytes + "\n"):
          #We are about to return the whole randNum we made
          #Check run count so we know when to clear randNum
          #If we clear it too soon, we'll end up wasting
          #elements from the randBits file.
          if(self.run == 0):
            self.run = 1
          else:
            self.run = 0
            self.randBytes = ''
          
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
