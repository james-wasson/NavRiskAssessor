import json
import re
import datetime
import math



from apixu.client import ApixuClient, ApixuException
api_key = '2748c70af4ea49e39f3171813170911'
client = ApixuClient(api_key)

maxDist = 160;
def distCalc(dist):
  return (maxDist - dist)/maxDist

def wasOutOfState(state):
  return state != 'MD'

def getDistance(lat1, lon1, lat2, lon2):
  # approximate radius of earth in km
  R = 6373.0

  lat1 = math.radians(lat1)
  lon1 = math.radians(lon1)
  lat2 = math.radians(lat2)
  lon2 = math.radians(lon2)

  dlon = lon2 - lon1
  dlat = lat2 - lat1

  a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

  return R * c

def isWeekend(stringDate):

  return date.weekday() >= 5 or (date.weekday() >= 4 and date.hour > 18)

inF = open("normalizedData.json", 'r')
outF= open("cs437WeatherInfo.json", 'w')
s = ""
t = ""
for l in inF:
  s += l
  if (l.rstrip() == "},"):
    s = s.rstrip()[:-1]
    j = json.loads(s)
    lat = j['Latitude']
    long = j['Longitude']
    temp1 = datetime.datetime.strptime(j["Time"], "%Y-%m-%dT%H:%M:%S" )
    temp2 = temp1.isoformat()
    temp3 = temp2[0:10]
    x = (int(temp3[0:4]))
    y = (int(temp3[5:7]))
    z = (int(temp3[8:10]))
    date = (""+str(x)+"-"+str(y)+"-"+str(z))
    end = (""+str(x)+"-"+str(y)+"-"+str(z+1))
    past = client.getHistoryWeather(q=(lat,long) , dt=date)
    j['Weather'] = [{
                    'Condition' : str(past['forecast']['forecastday'][0]['day']['condition']['text']),
                    'Max Temperature Celcius' : str(past['forecast']['forecastday'][0]['day']['maxtemp_c']),
                    'Min Temperature Celcius' : str(past['forecast']['forecastday'][0]['day']['mintemp_c']),
                    'Average Temperature Celcius' : str(past['forecast']['forecastday'][0]['day']['avgtemp_c']),
                    'Total Precipitation Millimeters' : str(past['forecast']['forecastday'][0]['day']['totalprecip_mm'])}]

      
    outF.write(json.dumps(j, sort_keys=True, indent=2) + ",\n")
    s = ""
    
