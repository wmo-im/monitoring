import urllib.request
import json
import sys
from countrycode import countrycode

URL="https://oscar.wmo.int/surface/rest/api/search/station?wigosId="
countries={}
cnames={}

def get_cname(wsi,tsi):
  print("Searching country for: "+str(wsi)+" "+str(tsi),file=sys.stderr)
  try:
    cname=cnames[wsi]
    print("Got: "+str(cname),file=sys.stderr)
    return cname
  except:
    country=str(get_country(wsi,tsi))
    cnameu=countrycode.countrycode(codes=[country], origin='country_name', target='iso3c')[0]
    try:
      cname=cnameu.lower()
    except:
      cname=cnameu
    cnames[wsi]=cname
    return cname

def get_country(wsi,tsi):
  if (wsi==None):
    if (tsi):
      wsi="0-20000-0-"+tsi
    
  if (wsi==None):
    return None
  else:
    try:
      country=countries[wsi]
      return country
    except:
      print("Searching country: "+URL+wsi,file=sys.stderr)
      try:
        contents = urllib.request.urlopen(URL+wsi).read()
        contents=json.loads(contents.decode())
        contents=contents["stationSearchResults"]
        contents=contents[0]
        country=contents["territory"]
      except:
        country=None
      print("Got: "+str(country),file=sys.stderr)
      countries[wsi]=country
    return country

