#!/usr/bin/env python3
import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
import json
import getopt
import sys

sensor = ''
baseline = ''
data = ''
totals_a_gauge=None
totals_b_gauge=None
percentage_gauge=None
stations_a_gauge=None
stations_b_gauge=None
lat_gauge=None
lon_gauge=None
stations_p_gauge=None
port=9877

def init():
   global totals_a_gauge
   global totals_b_gauge
   global percentage_gauge
   global stations_a_gauge
   global stations_b_gauge
   global lat_gauge
   global lon_gauge
   global stations_p_gauge

   totals_a_gauge=Gauge("wmo_wis2_base_count_by_country", "Number of Stations (expected)", ["sensor","center"])
   totals_b_gauge=Gauge("wmo_wis2_data_count_by_country", "Number of Stations (is)", ["sensor","center"])
   percentage_gauge=Gauge("wmo_wis2_percentage_by_country", "Percentage received", ["sensor","center"])
   stations_a_gauge=Gauge("wmo_wis2_base_count_by_station", "Number of Observations from Station (expected)", ["sensor","center","id","latitude","longitude"])
   stations_b_gauge=Gauge("wmo_wis2_data_count_by_station", "Number of Observations from Station (is)", ["sensor","center","id","latitude","longitude"])
   stations_p_gauge=Gauge("wmo_wis2_percentage_by_station", "Percentage received per Station", ["sensor","center","id","latitude","longitude"])
   lat_gauge=Gauge("wmo_wis2_latitude_by_station", "Latitude of Station", ["sensor","center","id"])
   lon_gauge=Gauge("wmo_wis2_longitude_by_station", "Longitude of Station", ["sensor","center","id"])

def main(argv):
   global sensor
   global baseline
   global data
   global totals_a_gauge
   global totals_b_gauge
   global percentage_gauge
   global stations_a_gauge
   global stations_b_gauge
   global lat_gauge
   global lon_gauge
   global stations_p_gauge
   
   countries=[] 
   stationids=[]
   totals_a={}
   totals_b={}
   percentage={}
   lat={}
   lon={}
   stations_a={}
   stations_b={}
   stations_p={}

   inputfile = ''
   cfg={}
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print('exporter.py -f <Config File>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('exporter.py -f <Config File>')
         sys.exit()
      elif opt in ("-f", "--file"):
         inputfile = arg
   if (inputfile == ''):
      print('exporter.py -f <Config File>')
      sys.exit(2)

   if (not os.path.isfile(inputfile)):
     print(inputfile+' not found')
     sys.exit(2)

   try: 
     with open(inputfile, 'rb') as fin:
       cfg = json.load(fin)
  
     port = cfg['exporter']['port']
     sensor = cfg['exporter']['sensor']
     baseline = cfg['exporter']['baseline']
     data = cfg['exporter']['data']
   except Exception as e:
     print("Fileformat Error in "+inputfile,file=sys.stderr)
     print(e)
     sys.exit(2)

   try: 
     start_http_server(port)
   except:
      print("Can not listen on "+port)
      sys.exit(3)

   if (not os.path.isfile(baseline)):
     print(baseline+' not found')
     sys.exit(2)
   if (not os.path.isfile(data)):
     print(data+' not found')
     sys.exit(2)

   init()

   while True:
        print("Getting Metrics...",file=sys.stderr,end=' ')
        sys.stderr.flush()
       
        try:
          with open(baseline, 'rb') as fin:
            base = json.load(fin)["features"]
        except:
          base=[]
        try:
          with open(data, 'rb') as fin:
            mon = json.load(fin)["features"]
        except:
          mon=[]

        for country in countries:
          totals_a[country].set(0)
        for station in stationids:
          stations_a[station].set(0)
        for item in base:
          c=item["properties"]["country"]
          if not c in countries:
             countries.append(c) 
             totals_a[c]=totals_a_gauge.labels(sensor,c)
             totals_a[c].set(0)
             totals_b[c]=totals_b_gauge.labels(sensor,c)
             totals_b[c].set(0)
             percentage[c]=percentage_gauge.labels(sensor,c)
             percentage[c].set(0)
          totals_a[c].inc(1)
          try:
            c=item["properties"]["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["properties"]["stationid"]
            except:
              c="None"
          if not c in stationids:
             stationids.append(c) 
             stations_a[c]=stations_a_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_a[c].set(0)
             stations_b[c]=stations_b_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_b[c].set(0)
             stations_p[c]=stations_p_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_p[c].set(0)
             lat[c]=lat_gauge.labels(sensor,item["properties"]["country"],c)
             lon[c]=lon_gauge.labels(sensor,item["properties"]["country"],c)
          stations_a[c].inc(1)
          lat[c].set(item["geometry"]["coordinates"][1])
          lon[c].set(item["geometry"]["coordinates"][0])
          
        for country in countries:
          totals_b[country].set(0)
        for station in stationids:
          stations_b[station].set(0)
        for item in mon:
          c=item["properties"]["country"]
          if not c in countries:
             countries.append(c) 
             totals_a[c]=totals_a_gauge.labels(sensor,c)
             totals_a[c].set(0)
             totals_b[c]=totals_b_gauge.labels(sensor,c)
             totals_b[c].set(0)
             percentage[c]=percentage_gauge.labels(sensor,c)
             percentage[c].set(0)
          totals_b[c].inc(1)
          try:
            c=item["properties"]["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["properties"]["stationid"]
            except:
              c="None"
          if not c in stationids:
             stationids.append(c) 
             stations_a[c]=stations_a_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_a[c].set(0)
             stations_b[c]=stations_b_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_b[c].set(0)
             stations_p[c]=stations_p_gauge.labels(sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stations_p[c].set(0)
             lat[c]=lat_gauge.labels(sensor,item["properties"]["country"],c)
             lon[c]=lon_gauge.labels(sensor,item["properties"]["country"],c)
          stations_b[c].inc(1)
          lat[c].set(item["geometry"]["coordinates"][1])
          lon[c].set(item["geometry"]["coordinates"][0])

        for country in countries:
          try:
            percentage[country].set(totals_b[country]._value.get()/totals_a[country]._value.get()*100)
          except:
            percentage[country].set(100)
        
        for station in stationids:
          try:
            stations_p[station].set(stations_b[station]._value.get()/stations_a[station]._value.get()*100)
          except:
            stations_p[station].set(100)
        print("done",file=sys.stderr)
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])
