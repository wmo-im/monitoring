import urllib.request
import json
import sys

URL="https://oscar.wmo.int/surface/rest/api/search/station?wigosId="
countries={}

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
      contents = urllib.request.urlopen(URL+wsi).read()
      contents=json.loads(contents.decode())
      try:
        contents=contents["stationSearchResults"]
        contents=contents[0]
        country=contents["territory"]
      except:
        country=None
      print("Searching country: "+URL+wsi,file=sys.stderr)
      countries[wsi]=country
    return country

