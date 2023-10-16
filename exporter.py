#!/venv/bin/python3
import os
import time
import prometheus_client as client
import requests
import json
import getopt
import sys

sensor = ''
baseline = ''
data = ''
port=9877

class monilabel:
        labels=None
        unusedcount=0
        mybasegauge=None
        mydatagauge=None
        mypercentgauge=None
        mybasegaugelabel=None
        mydatagaugelabel=None
        mypercentgaugelabel=None

        def set_base(self,value):
            self.mybasegaugelabel.set(value)
        def set_data(self,value):
            self.mydatagaugelabel.set(value)
        def set_percent(self,value):
            self.mypercentgaugelabel.set(value)
        def inc_base(self,value):
            self.mybasegaugelabel.inc(value)
            self.unusedcount=0
        def inc_data(self,value):
            self.mydatagaugelabel.inc(value)
            self.unusedcount=0
        def get_base(self):
            return self.mybasegaugelabel._value.get()
        def get_data(self):
            return self.mydatagaugelabel._value.get()
                   
        def __init__(self,base,data,percent,args):
            self.labels=args
            self.mybasegauge=base
            self.mydatagauge=data
            self.mypercentgauge=percent
            self.mybasegaugelabel=self.mybasegauge.labels(*args)
            self.mydatagaugelabel=self.mydatagauge.labels(*args)
            self.mypercentgaugelabel=self.mypercentgauge.labels(*args)
            self.set_base(0)
            self.set_data(0)
            self.set_percent(0)
        
        def deleted(self):
            self.unusedcount+=1
            if self.unusedcount>10:
               self.mybasegauge.remove(*self.labels)
               self.mydatagauge.remove(*self.labels)
               self.mypercentgauge.remove(*self.labels)
               return True
            return False

class monimetric:
        base_gauge=None
        data_gauge=None
        percentage_Gauge=None
        labels=None
	
        def __init__(self,name_a,name_b,name_p,text_a,text_b,text_p,keys):
                self.base_gauge=client.Gauge(name_a,text_a,keys)
                self.data_gauge=client.Gauge(name_b,text_b,keys)
                self.percentage_gauge=client.Gauge(name_p,text_p,keys)
                self.labels={}

        def set_base(self,id,value):
                self.labels[id].set_base(value)
        def set_data(self,id,value):
                self.labels[id].set_data(value)
        def set_percent(self,id,value):
                self.labels[id].set_percent(value)
        def inc_base(self,id,value):
                self.labels[id].inc_base(value)
        def inc_data(self,id,value):
                self.labels[id].inc_data(value)
        def update(self):
                for label in self.labels:
                  try:
                    self.labels[label].set_percent(self.labels[label].get_data()/self.labels[label].get_base()*100)
                  except:
                    self.labels[label].set_percent(100)
        def add(self,id,b,d,*args):
                try:
                  self.inc_base(id,b)
                  self.inc_data(id,d)
                except:
                  self.labels[id]=monilabel(self.base_gauge,self.data_gauge,self.percentage_gauge,args)
                  self.inc_base(id,b)
                  self.inc_data(id,d)
        def clear(self):
            for label in self.labels.copy():
               if self.labels[label].deleted():
                  del self.labels[label]
               else:
                  self.labels[label].set_base(0)
                  self.labels[label].set_data(0)

def init():
   client.REGISTRY.unregister(client.PROCESS_COLLECTOR)
   client.REGISTRY.unregister(client.PLATFORM_COLLECTOR)
   client.REGISTRY.unregister(client.GC_COLLECTOR)
   global perStation
   perStation=monimetric("wmo_wis2_sensor_basecountbystation","wmo_wis2_sensor_datacountbystation","wmo_wis2_sensor_percentagebystation","Number of Observations from Station (expected)","Number of Observations from Station (is)","Percentage received per Station",["report_by","centre_id","country","id","latitude","longitude"])
   global perCountry
   perCountry=monimetric("wmo_wis2_sensor_basecountbycountry","wmo_wis2_sensor_datacountbycountry","wmo_wis2_sensor_percentagebycountry","Number of Stations (expected)","Number of Stations (is)","Percentage received",["report_by","centre_id","country"])

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
     sensor = cfg['exporter']['centre_id']
     baseline = cfg['exporter']['baseline']
     data = cfg['exporter']['data']
   except Exception as e:
     print("Fileformat Error in "+inputfile,file=sys.stderr)
     print("Missing entry",file=sys.stderr)
     print(e,file=sys.stderr)
     sys.exit(2)

   try: 
     client.start_http_server(port)
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
        perStation.clear()
        perCountry.clear()

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
          try:
            c=item["properties"]["country"]
          except:
            c="None"
          try:
            perCountry.add(c,1,0,sensor,item["properties"]["centre_id"],c)
          except:
            perCountry.add(c,1,0,sensor,"None",c)
          try:
            c=item["properties"]["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["properties"]["stationid"]
            except:
              c="None"
          try:
               try:
                 perStation.add(c,1,0,sensor,item["properties"]["centre_id"],item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
               except:
                 perStation.add(c,1,0,sensor,"None",item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
          except:
            pass
          
        for item in mon:
          try:
            c=item["properties"]["country"]
          except:
            c="None"
          try:
               perCountry.add(c,0,1,sensor,item["properties"]["centre_id"],c)
          except:
               perCountry.add(c,0,1,sensor,"None",c)
          try:
            c=item["properties"]["wigosid"]
          except:
            c="None"
          if ((not c) or (c=="None")):
            try:
              c=item["properties"]["stationid"]
            except:
              c="None"
          try:
               try:
                 perStation.add(c,0,1,sensor,item["properties"]["centre_id"],item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
               except:
                 perStation.add(c,0,1,sensor,"None",item["properties"]["country"],c,item["geometry"]["coordinates"][1],item["geometry"]["coordinates"][0])
          except:
            pass

        perCountry.update()
        
        perStation.update()
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])
