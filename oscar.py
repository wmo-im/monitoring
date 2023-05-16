import urllib.request
import json
import sys
from threading import Thread
from countrycode import countrycode
import time
import datetime

URL="https://oscar.wmo.int/surface/rest/api/search/station?wigosId="
URL2="https://oscar.wmo.int/surface/rest/api/stations/station/"

class oscar:
  cnames={}
  cids={}
  times={}
  writer=None
  cache=None

  def __init__(self,cache):
    self.cache=cache
    try:
      with open(cache,'r') as f:
          content=json.load(f)
      self.cnames=content["cnames"]
      self.cids=content["cids"]
      self.times=content["times"]
    except:
      self.cnames={}
      self.cids={}
      self.times={}
    self.writer=Thread(target = self.write,daemon=True)
    self.writer.start()

  def get_cname(self,wsi,tsi):
    if (wsi==None):
      if (tsi):
        wsi="0-20000-0-"+str(tsi)
    
    wsi=str(wsi)
    print("Searching country for: "+wsi,file=sys.stderr)
    try:
      dtnow=datetime.datetime.utcnow()
      now=int(dtnow.timestamp())
      cname=self.cnames[wsi]
      if (cname == "None"):
        if (now-self.times[wsi]>7*24*60*60):
          raise Exception("Reload entry")
      print("Got: "+str(cname),file=sys.stderr)
      return cname
    except Exception as e:
      print(e)
      country=self.get_country(wsi)
      cnameu=countrycode.countrycode(codes=[country], origin='country_name', target='iso3c')[0]
      try:
        cname=cnameu.lower()
      except:
        cname=cnameu
      cname=str(cname)
      self.cnames[wsi]=cname
      print("Got: "+str(cname),file=sys.stderr)
      return cname

  def get_cid(self,wsi,tsi):
    if (wsi==None):
      if (tsi):
        wsi="0-20000-0-"+str(tsi)
    
    wsi=str(wsi)
    print("Searching id for: "+wsi,file=sys.stderr)
    try:
      cid=self.cids[wsi]
      print("Got: "+str(cid),file=sys.stderr)
      return cid
    except:
      country=self.get_country(wsi)
      try:
        self.cid=cids[wsi]
        print("Got: "+str(cid),file=sys.stderr)
        return cid
      except:
        cid=None
        return cid

  def get_country(self,wsi):
    if (wsi==None):
      return None
    else:
      print("Searching country: "+URL+wsi,file=sys.stderr)
      try:
        contents = urllib.request.urlopen(URL+wsi).read()
        contents=json.loads(contents.decode())
        contents=contents["stationSearchResults"]
        contents=contents[0]
        country=contents["territory"]
      except:
        country=None
      try:
        ids=contents["id"]
        print("->"+URL2+str(ids)+"/stationReport")
        contents = urllib.request.urlopen(URL2+str(ids)+"/stationReport").read()
        contents=json.loads(contents.decode())
        contents=contents["organizations"]
        contents=contents[0]
        ids=contents["organizationName"]
      except:
        ids=None
      self.cids[wsi]=str(ids)
      country=str(country)
      if (country=="Türkiye"):
        country="Turkey"
      print("Got: "+country,file=sys.stderr)
      dtnow=datetime.datetime.utcnow()
      now=int(dtnow.timestamp())
      self.times[wsi]=now
      return country

  def write(self):
    while True:
      time.sleep(300)
      print("Caching oscar to "+str(self.cache))
      content={}
      content["cnames"]=self.cnames
      content["cids"]=self.cids
      content["times"]=self.times
      try:
        with open(self.cache,'w') as f:
          json.dump(content,f,ensure_ascii=False, indent=4)
      except:
        pass
