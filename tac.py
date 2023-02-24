#!/usr/bin/env python3

import os
import sys
import re
from datetime import datetime

#Reads a Synop file and prints the contents
def read_synop(f,stats,geo,s,inline):
  entry={}
  lat=""
  lon=""
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
    if not ("NIL") in s[2]:
      if not ("NNNN") in s[2]:
        print("No station data for: "+s[2]+" in "+f,file=sys.stderr)
  entry["time"]=time
  if (latlon != None): 
    entry["stationid"]=s[2]
    lat=latlon[0]
    lon=latlon[1]
    geo["geometry"]["coordinates"]=[lon,lat]
  else:
    geo["geometry"]["coordinates"]=None
  geo["properties"]=entry

#Reads a Ship file and prints the contents
def read_ship(f,geo,s,inline):
  entry={}
  lat=""
  lon=""
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
      if not ("NIL") in s[1]:
        print("No coordinates for: "+s[1]+" in "+f,file=sys.stderr)
    entry["time"]=time
    if (latlon != None): 
      entry["stationid"]=s[1]
      lat=latlon[0]
      lon=latlon[1]
      geo["geometry"]["coordinates"]=[lon,lat]
    else:
      geo["geometry"]["coordinates"]=None
    geo["properties"]=entry
  except:
    if not ("NIL") in s[1]:
      print("No Time information or invalid synop: "+s[0]+" "+f,file=sys.stderr)

#Reads a temp file and prints the contents
def read_temp(f,stats,geo,s,inline):
  entry={}
  lat=""
  lon=""
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
    if not ("NIL") in s[2]:
      print("No station data for: "+s[2]+" in "+f,file=sys.stderr)
  entry["time"]=time
  if (latlon != None): 
    entry["stationid"]=s[2]
    lat=latlon[0]
    lon=latlon[1]
    geo["geometry"]["coordinates"]=[lon,lat]
  else:
    geo["geometry"]["coordinates"]=None
  geo["properties"]=entry

#Reads Legacy Volume A
def read_vola():
  lat=""
  lon=""
  stats = {}
  with open(os.path.dirname(os.path.realpath(__file__))+'/vola_legacy_report.txt', 'rb') as fin:
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
      
      stats[stat]=[lat,lon]
      inline=fin.readline()
  return stats
 

#Reads a TAC file and prints the contents
def read_tac(f):
  result=[]
  lat=""
  lon=""
  stats = read_vola()
  with open(f, 'rb') as fin:
    print("Reading "+f,file=sys.stderr)
    inline=" "
    try: 
      while (inline and (not ((inline.startswith("AAXX")) or (inline.startswith("BBXX")) or (inline.startswith("TT"))))):
        inline=fin.readline().decode()
    except:
      inline=''
    while inline:
      geo={}
      geo["type"]="Feature"
      geo["geometry"]={}
      geo["geometry"]["type"]="Point"
    
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
      if ("AAXX" in s[0]):
        read_synop(f,stats,geo,s,inline)
      if ("BBXX" in s[0]):
        read_ship(f,geo,s,inline)
      if ("TT" in s[0]):
        read_temp(f,stats,geo,s,inline)
     
      try: 
        geo["properties"]["data_format"]="TAC"
        geo["properties"]["received_date"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d')
        geo["properties"]["received_time"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%H%M')
        result.append(geo)
      except:
        print("Decoding error in "+f,file=sys.stderr)
      
      try: 
        inline=fin.readline().decode()
        if (inline and (not inline.isspace())):
          if (("AAXX" in s[0]) and (not ("AAXX" in inline))):
            inline="AAXX "+s[1]+" "+inline
          if (("BBXX" in s[0]) and (not ("BBXX" in inline))):
            inline="BBXX "+inline
          if (("TT" in s[0]) and (not ("TT" in inline))):
            inline="TTAA "+inline
        else:
         inline=''
      except:
        inline=''
  return result
