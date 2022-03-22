#!/usr/bin/env python3
import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
import json
import getopt
import sys
from countrycode import countrycode

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

def init():
   global totals_a_gauge
   global totals_b_gauge
   global percentage_gauge
   global stations_a_gauge
   global stations_b_gauge
   global lat_gauge
   global lon_gauge
   global stations_p_gauge

   totals_a_gauge=Gauge("base_count", "Number of Stations (expected)", ["location"])
   totals_b_gauge=Gauge("data_count", "Number of Stations (is)", ["location"])
   percentage_gauge=Gauge("percentage", "Percentage received", ["location"])
   stations_a_gauge=Gauge("base_observation_count", "Number of Observations from Station (expected)", ["id","latitude","longitude"])
   stations_b_gauge=Gauge("data_observation_count", "Number of Observations from Station (is)", ["id","latitude","longitude"])
   lat_gauge=Gauge("latitude", "Latitude of Station", ["id"])
   lon_gauge=Gauge("longitude", "Longitude of Station", ["id"])
   stations_p_gauge=Gauge("observation_percentage", "Percentage received per Station", ["id","latitude","longitude"])

def main(argv):
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

   start_http_server(9877)
   try:
      opts, args = getopt.getopt(argv,"hb:d:",["baseline=","data="])
   except getopt.GetoptError:
      print('exporter.py -b <Baseline> -d <Datar>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('exporter.py -b <Baseline> -d <Data>')
         sys.exit()
      elif opt in ("-b", "--baseline"):
         baseline = arg
      elif opt in ("-d", "--data"):
         data = arg
   if (baseline == ''):
      print('exporter.py -b <Baseline> -d <Data>')
      sys.exit(2)
   if (data == ''):
      print('exporter.py -b <Baseline> -d <Data>')
      sys.exit(2)

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
            base = json.load(fin)
        except:
          base=[]
        try:
          with open(data, 'rb') as fin:
            mon = json.load(fin)
        except:
          mon=[]

        for country in countries:
          totals_a[country].set(0)
        for station in stationids:
          stations_a[station].set(0)
        for item in base:
          c=item["country"]
          if not c in countries:
             countries.append(c) 
             cname=countrycode.countrycode(codes=[c], origin='country_name', target='iso2c')[0]
             totals_a[c]=totals_a_gauge.labels(cname)
             totals_a[c].set(0)
             totals_b[c]=totals_b_gauge.labels(cname)
             totals_b[c].set(0)
             percentage[c]=percentage_gauge.labels(cname)
             percentage[c].set(0)
          totals_a[c].inc(1)
          try:
            c=item["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["stationid"]
            except:
              c="None"
          if not c in stationids:
             stationids.append(c) 
             stations_a[c]=stations_a_gauge.labels(c,item["lat"],item["lon"])
             stations_a[c].set(0)
             stations_b[c]=stations_b_gauge.labels(c,item["lat"],item["lon"])
             stations_b[c].set(0)
             stations_p[c]=stations_p_gauge.labels(c,item["lat"],item["lon"])
             stations_p[c].set(0)
             lat[c]=lat_gauge.labels(c)
             lon[c]=lon_gauge.labels(c)
          stations_a[c].inc(1)
          lat[c].set(item["lat"])
          lon[c].set(item["lon"])
          
        for country in countries:
          totals_b[country].set(0)
        for station in stationids:
          stations_b[station].set(0)
        for item in mon:
          c=item["country"]
          if not c in countries:
             countries.append(c) 
             cname=countrycode.countrycode(codes=[c], origin='country_name', target='iso2c')[0]
             totals_a[c]=totals_a_gauge.labels(cname)
             totals_a[c].set(0)
             totals_b[c]=totals_b_gauge.labels(cname)
             totals_b[c].set(0)
             percentage[c]=percentage_gauge.labels(cname)
             percentage[c].set(0)
          totals_b[c].inc(1)
          try:
            c=item["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["stationid"]
            except:
              c="None"
          if not c in stationids:
             stationids.append(c) 
             stations_a[c]=stations_a_gauge.labels(c,item["lat"],item["lon"])
             stations_a[c].set(0)
             stations_b[c]=stations_b_gauge.labels(c,item["lat"],item["lon"])
             stations_b[c].set(0)
             stations_p[c]=stations_p_gauge.labels(c,item["lat"],item["lon"])
             stations_p[c].set(0)
             lat[c]=lat_gauge.labels(c)
             lon[c]=lon_gauge.labels(c)
          stations_b[c].inc(1)
          lat[c].set(item["lat"])
          lon[c].set(item["lon"])

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
