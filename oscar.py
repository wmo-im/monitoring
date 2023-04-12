import urllib.request
import json
import sys
from countrycode import countrycode

URL="https://oscar.wmo.int/surface/rest/api/search/station?wigosId="
cnames={}

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
    return cname

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
      contents=None
    except:
      country=None
    country=str(country)
    print("Got: "+country,file=sys.stderr)
    return country

