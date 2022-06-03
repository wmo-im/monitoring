#!/usr/bin/env python3

import os
import sys
import re
from datetime import datetime

#Reads a TAC Synop file and prints the contents
def read_tac(f):
  result=[]
  geo={}
  entry={}
  lat=""
  lon=""
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
      
      stats[stat]=[lat,lon]
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
      geo["type"]="Feature"
      geo["geometry"]={}
      geo["geometry"]["type"]="Point"
      entry["data_format"]="TAC"
      entry["received_date"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d')
      entry["received_time"]=datetime.fromtimestamp(os.path.getmtime(f)).strftime('%H%M')
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
          print("No station data or invalid synop: "+s[2]+" in "+f,file=sys.stderr)
        if (latlon != None): 
          entry["time"]=time
          entry["stationid"]=s[2]
          lat=latlon[0]
          lon=latlon[1]
          geo["properties"]=entry
          geo["geometry"]["coordinates"]=[lon,lat]
          result.append(geo)
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
            print("No station data or invalid synop: "+s[1]+" in "+f,file=sys.stderr)
          if (latlon != None): 
            entry["time"]=time
            entry["stationid"]=s[1]
            geo["properties"]=entry
            geo["geometry"]["coordinates"]=[lon,lat]
            result.append(geo)
        except:
            print("No Time information or invalid synop: "+s[0]+" "+f,file=sys.stderr)
      try: 
        inline=fin.readline().decode()
        if (inline and (not inline.isspace())):
          if (("AAXX" in s[0]) and (not ("AAXX" in inline))):
            inline="AAXX "+s[1]+" "+inline
          if (("BBXX" in s[0]) and (not ("BBXX" in inline))):
            inline="BBXX "+inline
          if (("TTAA" in s[0]) and (not ("TTAA" in inline))):
            inline="TTAA "+inline
          if (("TTDD" in s[0]) and (not ("TTDD" in inline))):
            inline="TTDD "+inline
        else:
         inline=''
      except:
        inline=''
  return result

