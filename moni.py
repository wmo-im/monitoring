#!/usr/bin/env python3

from eccodes import *
import os
import sys
import getopt
import json
import re
from datetime import datetime

missing=2147483647

#Reads a BUFR file and prints the listed keys
def read_bufr(f,keys):
  with open(f, 'rb') as fin:
    msgid = None
    try:
      cnt = 0
      while 1:
        msgid = codes_bufr_new_from_file(fin)
        if msgid is None:
            break
        sn = codes_get(msgid, 'numberOfSubsets')
        codes_set(msgid, 'unpack', 1)
        compressed = codes_get(msgid, 'compressedData')
        num = 1
        while num<=sn:
          line="BUFR;"+f+';'+datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d;%H%M')
          for key1 in keys:
            if (type(key1)==str):
              key1=[key1]
            line+=';'
            for key2 in key1:
              try:
                if compressed:
                  val = codes_get_array(msgid, key2).tolist()
                  #I know this is not 100% correct, but it works for now
                  if(len(val)<sn):
                    val=val[0]
                  else:
                    val = val[num-1]
                else:
                  val = codes_get(msgid, '/subsetNumber='+str(num)+'/'+key2)
              except KeyValueNotFoundError:
                val=''
                print('Key '+key2+' not found in '+f, file=sys.stderr)
              except:
                val=''
                print('Decoding error on '+key2+' in '+f, file=sys.stderr)
              if((val!='') and (int(val)>=missing)):
                val=''
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
 
#Reads a GRIB file and prints the listed keys
def read_grib(f,keys):
  with open(f, 'rb') as fin:
    msgid = None
    try:
      cnt = 0
      while 1:
        msgid = codes_grib_new_from_file(fin)
        if msgid is None:
            break
        print(cnt)
        line="GRIB;"+f+';'+datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d;%H%M')
        for key1 in keys:
          if (type(key1)==str):
            key1=[key1]
          line+=';'
          for key2 in key1:
            try:
                val = codes_get(msgid, key2)
            except KeyValueNotFoundError:
                val=''
                print('Key '+key2+' not found in '+f, file=sys.stderr)
            if(val != ''):
              val=str(val).zfill(2);
              line+=val;
        print(line)
        if (not msgid is None):
          codes_release(msgid)
          msgid = None
    except:
      print(f+' does not look like GRIB', file=sys.stderr)
      if (not msgid is None):
        codes_release(msgid)
  
#Reads a TAC Synop file and prints the listed keys
def read_tac(f,keys):
  stats = {}
  with open('./vola_legacy_report.txt', 'rb') as fin:
    inline=fin.readline()
    inline=fin.readline()
    while inline:
      elems = inline.split(b'\t')
      stat=elems[5].decode()
      latm=elems[8].decode()
    
      deg,minutes,seconds,direction=re.split(" (\d+) (\d+)",latm)
      lat=(float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
      lonm=elems[9].decode()
      deg,minutes,seconds,direction=re.split(" (\d+) (\d+)",lonm)
      lon=(float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
      
      stats[stat]=str(lat)+';'+str(lon)
      inline=fin.readline()
  
  with open(f, 'rb') as fin:
    print("Reading "+f,file=sys.stderr)
    inline=" "
    try: 
      while (inline and (not (("AAXX" in inline) or ("BBXX" in inline) or ("TTAA" in inline) or ("TTDD" in inline)))):
        inline=fin.readline().decode()
    except:
      inline=''
    while inline:
      line="TAC;"+f+';'+datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d;%H%M')
      inline=' '.join(inline.split())
      s=inline.split(' ')
      nex=inline
      while (nex and (not ("=" in inline))):
        inline.rstrip()
        try:
          nex=fin.readline().decode()
          inline=inline+" "+nex
        except:
          nex=None
        inline=' '.join(inline.split())
        s=inline.split(' ')
      if (("AAXX" in s[0]) or ("TTDD" in s[0]) or ("TTAA" in s[0])):
        time=s[1]
        if (len(time) >= 7):
          time=time[2:6]
        else:
          time=time[2:4]
          time=time+"00" 
        try:
          latlon=stats[s[2]] 
        except:
          latlon=None
          print("No station data or invalid synop: "+s[2]+" "+f,file=sys.stderr)
        if (latlon != None): 
          line=line+';;'+time+';;'+s[2]+';'+latlon
          print(line)
      if ("BBXX" in s[0]):
        try:
          time=s[2]
          if (len(time) >= 7):
            time=time[2:6]
          else:
            time=time[2:4]
            time=time+"00" 
          try:
            lat=s[3]
            lat=lat[2:]
            lon=s[4]
            d=lon[0:1]
            lon=lon[1:]
            lat=float(lat)
            lat=lat/10
            lon=float(lon)
            lon=lon/10
            if(d=="3"):
              lat=-lat
            if(d=="5"):
              lat=-lat
              lon=-lon
            if(d=="7"):
              lon=-lon
            latlon=str(lat)+";"+str(lon)
          except:
            latlon=None
            print("No station data or invalid synop: "+s[1]+f,file=sys.stderr)
          if (latlon != None): 
            line=line+';;'+time+';;'+s[1]+';'+latlon
            print(line)
        except:
            print("No Time information or invalid synop: "+s[0]+" "+f,file=sys.stderr)
      try: 
        inline=fin.readline().decode()
        if (inline and (not inline.isspace())):
          if ("AAXX" in s[0]):
            inline="AAXX "+s[1]+" "+inline
          if ("BBXX" in s[0]):
            inline="BBXX "+inline
        else:
         inline=''
      except:
        inline=''

#Reads a directory and directs reading of files depending on the datatype
def read_dir(directory,datatype,keys):
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
      func(directory+"/"+f,keys)


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

