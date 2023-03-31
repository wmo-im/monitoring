#!/usr/bin/env python3

import os
import sys
import getopt
import json
import shutil
import datetime
import time
from bufr import read_bufr
from grib import read_grib
from tac import read_tac

#Reads a directory and directs reading of files depending on the datatype
def read_dir(directory,datatype,done):
  result = []
  fa = []
  if (not os.path.isdir(directory)):
    print(directory+" not found "+directory, file=sys.stderr)
 
  for (dirpath, dirnames, filenames) in os.walk(directory):
    fa.extend(filenames)
    break
 
  func=None
  if(datatype == 'BUFR'):
    func=read_bufr
  
  if(datatype == 'GRIB'):
    func=read_grib
  
  if(datatype == 'TAC'):
    func=read_tac
  
  if (func==None):
     print(datatype+' is not supported '+f, file=sys.stderr)
  else:
    for f in fa:
      if not f.startswith("."):
        try:
          result+=func(directory+"/"+f)
        except Exception as e:
          print("Error reading "+f,file=sys.stderr)
          print(e,file=sys.stderr)
        try:
          shutil.move(directory+"/"+f,done+"/"+f)
        except Exception as e:
          print("Error reading "+f,file=sys.stderr)
          print(e,file=sys.stderr)
  
  return result


def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print('reader.py -f <Config File>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('reader.py -f <Config File>')
         sys.exit()
      elif opt in ("-f", "--file"):
         inputfile = arg
   if (inputfile == ''):
      print('reader.py -f <Config File>')
      sys.exit(2)

   if (not os.path.isfile(inputfile)):
     print(inputfile+' not found')
     sys.exit(2)

   try: 
     with open(inputfile, 'rb') as fin:
       data = json.load(fin)
  
     outputfile = data['out']['file']
     keep = int(data['out']['keep'])
     data=data['monitor']
   except Exception as e:
     print("Fileformat Error in "+inputfile,file=sys.stderr)
     print(e,file=sys.stderr)
     sys.exit(2)
  
   result=[]
   geo={}
   if (os.path.isfile(outputfile)):
     try:
       with open(outputfile, 'rb') as fin:
         result = json.load(fin)['features']
     except:
       print("Fileformat Error in "+outputfile,file=sys.stderr)
       sys.exit(2)
 
   for el in data: 
     if (not os.path.isdir(el['done'])):
       try:
         os.mkdir(el['done'])
       except:
         print("Error at mkdir "+el['done'],file=sys.stderr)
         sys.exit(1)
     print("Scanning "+el['directory'])

     result+=read_dir(el['directory'],el['format'],el['done'])
  
   dtnow=datetime.datetime.utcnow()
   now=dtnow.hour*100+dtnow.minute
   geo["type"]="FeatureCollection"
   geo["features"]=[]
   for el in result:
     try:
       age=int(el["properties"]["received_time"])
       age=now-age
       if(age<0):
         age+=2400
       age/=100
     except:
       age=keep+1
     if(age<=keep):
       geo["features"].append(el)
  
   try:
     with open(outputfile, 'w', encoding='utf-8') as fout:
       json.dump(geo, fout, ensure_ascii=False, indent=4)
       print("",file=fout)
   except:
     print("Error in writing "+outputfile,file=sys.stderr)
     sys.exit(2)
   del result
   del geo


if __name__ == "__main__":
   main(sys.argv[1:])

