#!/usr/bin/env python3

import os
import sys
import getopt
import json
from bufr import read_bufr
from grib import read_grib
from tac import read_tac
from oscar import get_country
      
#Reads a directory and directs reading of files depending on the datatype
def read_dir(directory,datatype,keys):
  result = []
  fa = []
  if (not os.path.isdir(directory)):
    print(directory+" not found "+f, file=sys.stderr)
 
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
      result+=func(directory+"/"+f,keys)
  return result


def main(argv):
   inputfile = ''
   result=[]
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
     result+=read_dir(el['directory'],el['format'],el['keys'])
   
   for el in result:
     try:
       wsi=el["wigosid"]
     except:
       wsi=None
     try:
       tsi=el["stationid"]
     except:
       tsi=None
     country=str(get_country(wsi,tsi))
     el["country"]=country
   
   json_string=json.dumps(result,indent=4)
   print(json_string) 

   sys.exit()


if __name__ == "__main__":
   main(sys.argv[1:])

