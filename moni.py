#!/usr/bin/env python3

import os
import sys
import getopt
import json
import shutil
from bufr import read_bufr
from grib import read_grib
from tac import read_tac
from oscar import get_country
from countrycode import countrycode
      
#Reads a directory and directs reading of files depending on the datatype
def read_dir(directory,datatype,done):
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
      result+=func(directory+"/"+f)
      shutil.move(directory+"/"+f,done+"/"+f)
   
  return result


def main(argv):
   inputfile = ''
   result=[]
   geo={}
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
     if (not os.path.isdir(el['done'])):
       try:
         os.mkdir(el['done'])
       except:
         print("Error at mkdir "+el['done'])
         sys.exit(1)

     result+=read_dir(el['directory'],el['format'],el['done'])
   
   for el in result:
     try:
       wsi=el["properties"]["wigosid"]
     except:
       wsi=None
     try:
       tsi=el["properties"]["stationid"]
     except:
       tsi=None
     country=str(get_country(wsi,tsi))
     cname=countrycode.countrycode(codes=[country], origin='country_name', target='iso2c')[0]
     el["properties"]["country"]=cname
  
   geo["type"]="FeatureCollection"
   geo["features"]=result
   json_string=json.dumps(geo,indent=4)
   print(json_string) 

   sys.exit()


if __name__ == "__main__":
   main(sys.argv[1:])

