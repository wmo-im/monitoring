#!/usr/bin/env python3

from eccodes import *
import os
import sys
import getopt
import json
from datetime import datetime

#Reads a BUFR file and prints the listed keys
def read_bufr(f,keys):
  with open(f, 'rb') as fin:
    msgid = None
    try:
      cnt = 0
      while 1:
        msgid = codes_bufr_new_from_file(fin)
        sn = codes_get(msgid, 'numberOfSubsets')
        codes_set(msgid, 'unpack', 1)
        compressed = codes_get(msgid, 'compressedData')
        num = 1
        while num<=sn:
          line=f+';'+datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d;%H%M')
          for key1 in keys:
            if (type(key1)==str):
              key1=[key1]
            line+=';'
            for key2 in key1:
              try:
                if compressed:
                  val = codes_get(msgid, key)
                  val = val[num]
                else:
                  val = codes_get(msgid, '/subsetNumber='+str(num)+'/'+key2)
              except KeyValueNotFoundError:
                val=''
                print('Key '+key2+' not found in '+f, file=sys.stderr)
              if(val != ''):
                val=str(val).zfill(2);
              line+=val;
          num += 1
          print(line)
        if (not msgid is None):
          codes_release(msgid)
          msgid = None
    except:
      print(f+' does not look like BUFR', file=sys.stderr)
    if (not msgid is None):
      codes_release(msgid)
  

#Reads a directory and directs reading of files depending on the datatype
def read_dir(directory,datatype,keys):
  fa = []
  if (not os.path.isdir(directory)):
    print(directory+" not found", file=sys.stderr)
 
  for (dirpath, dirnames, filenames) in os.walk(directory):
    fa.extend(filenames)
    break
 
  func=None
  if(datatype == 'BUFR'):
    func=read_bufr
  
  if (func==None):
     print(datatype+' is not supported', file=sys.stderr)
  else:
    for f in fa:
      func(f,keys)


def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print('moni.py -f <Config File>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('moni.py -f <Config File>')
         sys.exit()
      elif opt in ("-f", "--file"):
         inputfile = arg
   if (inputfile == ''):
      print('moni.py -f <Config File>')
      sys.exit(2)

   if (not os.path.isfile(inputfile)):
     print(inputfile+' not found')
     sys.exit(2)

   with open(inputfile, 'rb') as fin:
     data = json.load(fin)
   
   data=data['monitor']

   for el in data: 
     read_dir(el['directory'],el['format'],el['keys'])
   
   sys.exit()




if __name__ == "__main__":
   main(sys.argv[1:])

