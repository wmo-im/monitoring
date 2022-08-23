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
port=9877

class monimetric:
        base_gauge=None
        data_gauge=None
        percentage_Gauge=None
        bases={}
        datas={}
        percents={}
	
        def __init__(self,name_a,name_b,name_p,text_a,text_b,text_p,keys):
                self.base_gauge=Gauge(name_a,text_a,keys)
                self.data_gauge=Gauge(name_b,text_b,keys)
                self.percentage_gauge=Gauge(name_p,text_p,keys)

        def set_base(self,id,value):
                self.bases[id].set(value)
        def set_data(self,id,value):
                self.datas[id].set(value)
        def set_percent(self,id,value):
                self.percents[id].set(value)
        def inc_base(self,id,value):
                self.bases[id].inc(value)
        def inc_data(self,id,value):
                self.datas[id].inc(value)
        def update(self,id):
                try:
                   self.percents[id].set(self.datas[id]._value.get()/self.bases[id]._value.get()*100)
                except:
                   self.percents[id].set(100)
        def add(self,id,*args):
                self.bases[id]=self.base_gauge.labels(*args)
                self.bases[id].set(0)
                self.datas[id]=self.data_gauge.labels(*args)
                self.datas[id].set(0)
                self.percents[id]=self.percentage_gauge.labels(*args)
                self.percents[id].set(0)
        def clear(self):
                self.base_gauge.clear()
                self.data_gauge.clear()
                self.percentage_gauge.clear()

def init():
   global perStation
   perStation=monimetric("wmo_wis2_base_count_by_station","wmo_wis2_data_count_by_station","wmo_wis2_percentage_by_station","Number of Observations from Station (expected)","Number of Observations from Station (is)","Percentage received per Station",["sensor","center","id","latitude","longitude"])
   global perCountry
   perCountry=monimetric("wmo_wis2_base_count_by_country","wmo_wis2_data_count_by_country","wmo_wis2_percentage_by_country","Number of Stations (expected)","Number of Stations (is)","Percentage received",["sensor","center"])

def main(argv):
   global sensor
   global baseline
   global data
   global perCountry
   global perStation
   
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
     keep = cfg['exporter']['keep']
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
        countries=[] 
        stationids=[]
        perStation.clear()
        perCountry.clear()

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

        for item in base:
          c=item["properties"]["country"]
          if not c in countries:
             perCountry.add(c,sensor,c)
             countries.append(c) 
          perCountry.inc_base(c,1)
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
             perStation.add(c,sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stationids.append(c) 
          perStation.inc_base(c,1)
          
        for country in countries:
          perCountry.set_data(country,0)
        for station in stationids:
          perStation.set_data(station,0)
        for item in mon:
          c=item["properties"]["country"]
          if not c in countries:
             perCountry.add(c,sensor,c)
             countries.append(c) 
          perCountry.inc_data(c,1)
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
             perStation.add(c,sensor,item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
             stationids.append(c) 
          perStation.inc_data(c,1)

        for country in countries:
          perCountry.update(country)
        
        for station in stationids:
          perStation.update(station)
        print("done",file=sys.stderr)
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])
