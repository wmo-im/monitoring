#!/usr/bin/env python3

from eccodes import *
import os
import sys
import re
from datetime import datetime


def get_key(f,msgid,key):
  try:
    val = codes_get(msgid, key)
  except KeyValueNotFoundError:
    val=''
    print('Key '+key+' not found in '+f, file=sys.stderr)
  return val

def get_date(f,msgid):
  date=""
  year=get_key(f,msgid,"year")
  month=get_key(f,msgid,"month")
  day=get_key(f,msgid,"day")
  if(year != ''):
    date+=str(year).zfill(2);
  if(month != ''):
    date+=str(month).zfill(2);
  if(day != ''):
    date+=str(day).zfill(2);
  return date

def get_time(f,msgid):
  time=""
  hour=get_key(f,msgid,"hour")
  minute=get_key(f,msgid,"minute")
  if(hour != ''):
    time+=str(hour).zfill(2);
  if(minute != ''):
    time+=str(minute).zfill(2);
  return time

#Reads a GRIB file and prints the listed keys
def read_grib(f,keys):
  result=[]
  entry={}
  with open(f, 'rb') as fin:
    msgid = None
    try:
      cnt = 0
      while 1:
        msgid = codes_grib_new_from_file(fin)
        if msgid is None:
            break
        entry["type"]="GRIB"
        entry["received_date"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d')
        entry["received_time"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%H%M')
        entry["date"]=get_date(f,msgid)
        entry["time"]=get_time(f,msgid)
        entry["centre"]=get_key(f,msgid,"centre")
        entry["generatingProcessIdentifier"]=get_key(f,msgid,"generatingProcessIdentifier")
        entry["lat"]=get_key(f,msgid,"latitudeOfFirstGridPoint")
        entry["lon"]=get_key(f,msgid,"longitudeOfFirstGridPoint")
        
        result.append(entry)
        if (not msgid is None):
          codes_release(msgid)
          msgid = None
    except:
      print(f+' does not look like GRIB', file=sys.stderr)
      if (not msgid is None):
        codes_release(msgid)
  return result
  
