#!/venv/bin/python3

import os
import sys
import getopt
import json
import subprocess
import time
from oscar import *

def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print('moni.py -f <Config File>')
      os._exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('moni.py -f <Config File>')
         os._exit()
      elif opt in ("-f", "--file"):
         inputfile = arg
   if (inputfile == ''):
      print('moni.py -f <Config File>')
      os._exit(2)

   if (not os.path.isfile(inputfile)):
     print(inputfile+' not found')
     os._exit(2)

   try: 
     with open(inputfile, 'rb') as fin:
       data = json.load(fin)
  
     outputfile = data['out']['file']
     keep = int(data['out']['keep'])
     cache=data['cache']
     data=data['monitor']
   except Exception as e:
     print("Fileformat Error in "+inputfile,file=sys.stderr)
     print(e,file=sys.stderr)
     os._exit(2)
  
   osc=oscar(cache)
   while True: 
     result=[]
     geo={}

     return_code = subprocess.call(str(os.path.realpath(os.path.dirname(__file__)))+"/reader.py "+" ".join(argv), shell=True)
     if (return_code != 0):
         print("Error with reader.py",file=sys.stderr)
         os._exit(2)

     if (os.path.isfile(outputfile+".tmp")):
       try:
         with open(outputfile+".tmp", 'rb') as fin:
           result = json.load(fin)['features']
       except:
         print("Fileformat Error in "+outputfile+".tmp",file=sys.stderr)
         os._exit(2)
 
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
       cname=osc.get_cname(wsi,tsi)
       cid=osc.get_cid(wsi,tsi)
       el["properties"]["country"]=cname
       el["properties"]["centre_id"]=cid
       geo["features"].append(el)
  
     try:
       with open(outputfile+".tmp", 'w', encoding='utf-8') as fout:
         json.dump(geo, fout, ensure_ascii=False, indent=4)
         print("",file=fout)
       os.unlink(outputfile)
       os.rename(outputfile+".tmp",outputfile)
     except:
       print("Error in writing "+outputfile,file=sys.stderr)
       os._exit(2)
     del result
     del geo
     print("Done")
     time.sleep(60)


if __name__ == "__main__":
   main(sys.argv[1:])

