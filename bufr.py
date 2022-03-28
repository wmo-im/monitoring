#!/usr/bin/env python3

from eccodes import *
import re
import sys
import os
from datetime import datetime

missing=2147483647

def get_key(f,msgid,compressed,num,sn,key):
  try:
    if compressed:
      val = codes_get_array(msgid, key).tolist()
      #I know this is not 100% correct, but it works for now
      if(len(val)<sn):
        val=val[0]
      else:
        val = val[num-1]
    else:
      val = codes_get(msgid, '/subsetNumber='+str(num)+'/'+key)
  except KeyValueNotFoundError:
    val=''
    print('Key '+key+' not found in '+f, file=sys.stderr)
  except:
    val=''
    print('Decoding error on '+key+' in '+f, file=sys.stderr)
  try:
    val2=int(val)
    if (val2>=missing):
      val=''
  except:
    pass 
  return val

def get_date(f,msgid,compressed,num,sn):
  date=""
  year=get_key(f,msgid,compressed,num,sn,"year")
  month=get_key(f,msgid,compressed,num,sn,"month")
  day=get_key(f,msgid,compressed,num,sn,"day")
  if(year != ''):
    date+=str(year).zfill(2);
  if(month != ''):
    date+=str(month).zfill(2);
  if(day != ''):
    date+=str(day).zfill(2);
  return date

def get_time(f,msgid,compressed,num,sn):
  time=""
  hour=get_key(f,msgid,compressed,num,sn,"hour")
  minute=get_key(f,msgid,compressed,num,sn,"minute")
  if(hour != ''):
    time+=str(hour).zfill(2);
  if(minute != ''):
    time+=str(minute).zfill(2);
  return time

def get_wsi(f,msgid,compressed,num,sn):
  wsi=str(get_key(f,msgid,compressed,num,sn,"wigosIdentifierSeries"))
  if (wsi):
    wsi+="-"+str(get_key(f,msgid,compressed,num,sn,"wigosIssuerOfIdentifier"))
    wsi+="-"+str(get_key(f,msgid,compressed,num,sn,"wigosIssueNumber"))
    wsi+="-"+str(get_key(f,msgid,compressed,num,sn,"wigosLocalIdentifierCharacter")).zfill(5)
    wsi=wsi.upper()
  else:
    wsi=None
  return wsi

def get_tsi(f,msgid,compressed,num,sn):
  tsi=get_key(f,msgid,compressed,num,sn,"blockNumber")
  if(tsi != ''):
    tsi=str(tsi).zfill(2);
  else:
    return None
  val=get_key(f,msgid,compressed,num,sn,"stationNumber")
  if(val != ''):
    val=str(val).zfill(3);
  else:
    return None
  tsi+=val;
  return tsi

#Reads and decodes a BUFR file 
def read_bufr(f):
  result=[]
  with open(f, 'rb') as fin:
    msgid = None
    try:
      cnt = 0
      while 1:
        geo={}
        entry={}
        msgid = codes_bufr_new_from_file(fin)
        if msgid is None:
            break
        sn = codes_get(msgid, 'numberOfSubsets')
        codes_set(msgid, 'unpack', 1)
        compressed = codes_get(msgid, 'compressedData')
        num = 1
        while num<=sn:
          geo["type"]="Feature"
          geo["geometry"]={}
          geo["geometry"]["type"]="Point"
          entry["type"]="BUFR"
          entry["received_date"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d')
          entry["received_time"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%H%M')
          entry["date"]=get_date(f,msgid,compressed,num,sn)
          entry["time"]=get_time(f,msgid,compressed,num,sn)
          entry["wigosid"]=get_wsi(f,msgid,compressed,num,sn)
          entry["stationid"]=get_tsi(f,msgid,compressed,num,sn)
          try:
            lat=float(get_key(f,msgid,compressed,num,sn,"latitude"))
            lon=float(get_key(f,msgid,compressed,num,sn,"longitude"))
          except:
            lat="-90"
            lon="0"

          geo["properties"]=entry
          geo["geometry"]["coordinates"]=[lon,lat]
          num += 1
          result.append(geo)
        if (not msgid is None):
          codes_release(msgid)
          msgid = None
    except:
      print(f+' does not look like BUFR', file=sys.stderr)
    if (not msgid is None):
      codes_release(msgid)
  return result 

