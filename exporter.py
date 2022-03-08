#!/usr/bin/env python3
import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
import json
import getopt
import sys

#        self.pending_requests.set(status_data["pending_requests"])
#        self.total_uptime.set(status_data["total_uptime"])
##        self.health.state(status_data["health"])

def main(argv):

   start_http_server(9877)
   baseline = ''
   data = ''
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

   with open(baseline, 'rb') as fin:
     base = json.load(fin)
   with open(data, 'rb') as fin:
     mon = json.load(fin)

   countries=[] 
   for item in base:
        c=item["country"]
        if not c in countries:
            countries.append(c) 
   for item in mon:
        c=item["country"]
        if not c in countries:
            countries.append(c) 
   
   totals_a={}
   totals_b={}
   percentage={}
   for country in countries:
        cname=country.replace(" ","_").replace(",","").replace("(","").replace(")","").replace("'","").replace("ô","")
        totals_a[country]=Gauge(cname+"_base_count", "Number of Stations (expected)")
        totals_b[country]=Gauge(cname+"_data_count", "Number of Stations (is)")
        percentage[country]=Gauge(cname+"_percentage", "Percentage received")

   while True:
        length = len(totals_a)
  
        for country in countries:
          totals_a[country].set(0)
          totals_b[country].set(0)
          percentage[country].set(0)
       
        with open(baseline, 'rb') as fin:
          base = json.load(fin)
        with open(data, 'rb') as fin:
          mon = json.load(fin)

        for item in base:
          c=item["country"]
          totals_a[c].inc(1)
        for item in mon:
          c=item["country"]
          totals_b[c].inc(1)

        for country in countries:
          percentage[country].set(totals_b[country]._value.get()/totals_a[country]._value.get()*100)
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])
