import urllib.request
import json
import sys
from countrycode import countrycode

URL="https://oscar.wmo.int/surface/rest/api/search/station?wigosId="
URL2="https://oscar.wmo.int/surface/rest/api/stations/station/"
cnames={}
cids={}

def get_cname(wsi,tsi):
  if (wsi==None):
    if (tsi):
      wsi="0-20000-0-"+str(tsi)
    
  wsi=str(wsi)
  print("Searching country for: "+wsi,file=sys.stderr)
  try:
    cname=cnames[wsi]
    print("Got: "+str(cname),file=sys.stderr)
    return cname
  except:
    country=get_country(wsi)
    cnameu=countrycode.countrycode(codes=[country], origin='country_name', target='iso3c')[0]
    try:
      cname=cnameu.lower()
    except:
      cname=cnameu
    cname=str(cname)
    cnames[wsi]=cname
    print("Got: "+str(cname),file=sys.stderr)
    return cname

def get_cid(wsi,tsi):
  if (wsi==None):
    if (tsi):
      wsi="0-20000-0-"+str(tsi)
    
  wsi=str(wsi)
  print("Searching id for: "+wsi,file=sys.stderr)
  try:
    cid=cids[wsi]
    print("Got: "+str(cid),file=sys.stderr)
    return cid
  except:
    country=get_country(wsi)
    try:
      cid=cids[wsi]
      print("Got: "+str(cid),file=sys.stderr)
      return cid
    except:
      cid=None
      return cid

def get_country(wsi):
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
    except Exception as e:
      ids=None
    cids[wsi]=str(ids)
    country=str(country)
    if (country=="Türkiye"):
      country="Turkye"
    print("Got: "+country,file=sys.stderr)
    return country

