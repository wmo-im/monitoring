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

def init():
   global countries
   global stationsids
   global totals_a
   global totals_b
   global percentage
   global lat
   global lon
   global stations_a
   global stations_b
   global stations_p

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

   for item in base:
        c=item["country"]
        if not c in countries:
            countries.append(c) 
        c=item["stationid"]
        if not c in stationids:
            stationids.append(c) 
   for item in mon:
        c=item["country"]
        if not c in countries:
            countries.append(c) 
        c=item["stationid"]
        if not c in stationids:
            stationids.append(c) 
   totals_a_gauge=Gauge("base_count", "Number of Stations (expected)", ["location"])
   totals_b_gauge=Gauge("data_count", "Number of Stations (is)", ["location"])
   percentage_gauge=Gauge("percentage", "Percentage received", ["location"])
   stations_a_gauge=Gauge("base_observation_count", "Number of Observations from Station (expected)", ["id"])
   stations_b_gauge=Gauge("data_observation_count", "Number of Observations from Station (is)", ["id"])
   lat_gauge=Gauge("latitude", "Latitude of Station", ["id"])
   lon_gauge=Gauge("longitude", "Longitude of Station", ["id"])
   stations_p_gauge=Gauge("observation_percentage", "Percentage received per Station", ["id"])
   for country in countries:
        cname=countrycode.countrycode(codes=[country], origin='country_name', target='iso2c')[0]
        totals_a[country]=totals_a_gauge.labels(cname)
        totals_b[country]=totals_b_gauge.labels(cname)
        percentage[country]=percentage_gauge.labels(cname)
   for station in stationids:
        stations_a[station]=stations_a_gauge.labels(station)
        stations_b[station]=stations_b_gauge.labels(station)
        stations_p[station]=stations_p_gauge.labels(station)
        lat[station]=lat_gauge.labels(station)
        lon[station]=lon_gauge.labels(station)

def main(argv):
   global baseline
   global data

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
        for country in countries:
          totals_a[country].set(0)
          totals_b[country].set(0)
          percentage[country].set(0)
        for station in stationids:
          stations_a[station].set(0)
          stations_b[station].set(0)
          stations_p[station].set(0)
       
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

        for item in base:
          c=item["country"]
          totals_a[c].inc(1)
          c=item["stationid"]
          stations_a[c].inc(1)
          lat[c].set(item["lat"])
          lon[c].set(item["lon"])
        for item in mon:
          c=item["country"]
          totals_b[c].inc(1)
          c=item["stationid"]
          stations_b[c].inc(1)
          lat[c].set(item["lat"])
          lon[c].set(item["lon"])

        for country in countries:
          try:
            percentage[country].set(totals_b[country]._value.get()/totals_a[country]._value.get()*100)
          except:
            percentage[country].set(100)
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])
