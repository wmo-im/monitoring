#!/usr/bin/env python3

import os
import sys
import getopt
import json
import subprocess
import time
from oscar import get_cname

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
  
   while True: 
     result=[]
     geo={}

     return_code = subprocess.call(str(os.path.realpath(os.path.dirname(__file__)))+"/reader.py "+" ".join(argv), shell=True)
     if (return_code != 0):
         print("Error with reader.py",file=sys.stderr)
         sys.exit(2)

     if (os.path.isfile(outputfile)):
       try:
         with open(outputfile, 'rb') as fin:
           result = json.load(fin)['features']
       except:
         print("Fileformat Error in "+outputfile,file=sys.stderr)
         sys.exit(2)
 
     geo["type"]="FeatureCollection"
     geo["features"]=[]
     for el in result:
       try:
         wsi=el["properties"]["wigosid"]
       except:
         wsi=None
       try:
         tsi=el["properties"]["stationid"]
       except:
         tsi=None
       cname=get_cname(wsi,tsi)
       el["properties"]["country"]=cname
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
     print("Done")
     time.sleep(60)


if __name__ == "__main__":
   main(sys.argv[1:])

