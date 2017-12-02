import json
import re
import sys
from math import sin, cos, sqrt, atan2, radians
import datetime
from datetime import date
from time import strftime
import holidays


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

roadDef = {
  "Avenue": "Ave",
  "Boulevard": "Blvd",
  "Circle": "Cir",
  "Drive": "Dr",
  "Pike": "Pike",
  "Way": "Way",
  "Lane": "Ln",
  "Place": "Pl",
  "Road": "Rd",
  "Route": ["Rt", "Rte"],
  "Street": "St",
  "Alley": "Aly",
}

highwayDef = {
  "Parkway": "Pkwy",
  "Broadway": "Bdwy",
  "Bypass": "Byp",
  "Causeway": "Cswy",
  "Expressway": "Expy",
  "Freeway": "Fwy",
  "Highway": "Hwy",
  "Motorway": "Mtwy",
  "Overpass": "Opas",
  "Trafficway": "Trfy",
  "Turnpike": "Tpk"
}

def categorizeRoad(s):
  returnVal = "";
  # determines if it is a road
  for key, val in roadDef.iteritems():
    if(findWholeWord(key)(s) or findWholeWord(key + ".")(s)):
      returnVal = "Road"
      break
    if type(val) is list or type(val) is tuple:
      for v in val:
        if(findWholeWord(v)(s) or findWholeWord(v + ".")(s)):
          returnVal = "Road"
          break;
    else:
      if(findWholeWord(val)(s) or findWholeWord(val + ".")(s)):
        returnVal = "Road"
        
    if (returnVal == "Road"):
      break;
      
  # determines if it is a highway
  for key, val in highwayDef.iteritems():
    if(findWholeWord(key)(s) or findWholeWord(key + ".")(s)):
      returnVal = "Highway"
      break
    if type(val) is list or type(val) is tuple:
      for v in val:
        if(findWholeWord(v)(s) or findWholeWord(v + ".")(s)):
          returnVal = "Highway"
          break;
    else:
      if(findWholeWord(val)(s) or findWholeWord(val + ".")(s)):
        returnVal = "Highway"
        
    if (returnVal == "Highway"):
      break;
  # sets default case and returns
  if (returnVal == ""):
    returnVal = "Road"
  return returnVal
      


def typeCategories(t, log):
  if t in log:
    return None
  if t in ["neighborhood", "point_of_interest", "establishment", "locality", "premise", "subpremise"]:
    return None
  if t in ["political", "embassy", "local_government_office", "city_hall" "courthouse"]:
    return "Political"
  if t in ["transit_station", "bus_station", "parking", "train_station", "car_rental", "subway_station", "travel_agency", "airport", "gas_station"]:
    return "Transit"
  if t in ["doctor", "health", "physiotherapist", "veterinary_care", "dentist"]:
    return "Doctor"
  if t in ["grocery_or_supermarket", "food", "restaurant", "cafe", "meal_delivery", "meal_takeaway", "bakery", "supermarket"]:
    return "Food"
  if t in ["store", "home_goods_store", "clothing_store", "furniture_store", "shoe_store", "shopping_mall", "electronics_store", "jewelry_store", "hardware_store", "pet_store", "department_store", "book_store", "bicycle_store", "movie_rental", "convenience_store"]:
    return "Store"
  if t in ["finance", "accounting", "lawyer", "pharmacy", "insurance_agency", "florist", "car_dealer", "real_estate_agency"]:
    return "Profession"
  if t in ["car_repair", "general_contractor", "moving_company", "painter", "electrician", "roofing_contractor", "plumber", "locksmith"]:
    return "Trade"
  if t in ["school", "police", "hospital", "post_office", "library", "university", "atm", "bank", "park", "cemetery", "art_gallery", "fire_station", "museum"]:
    return "Institution"
  if t in ["church", "place_of_worship", "synagogue", "mosque", "hindu_temple"]:
    return "Place_of_worship"
  if t in ["liquor_store", "bar", "night_club", "casino"]:
    return "Undesirable"
  if t in ["movie_theater", "stadium", "amusement_park", "natural_feature", "campground", "rv_park", "aquarium", "bowling_alley"]:
    return "Attraction"
  if t in ["storage", "car_wash", "lodging", "laundry", "funeral_home", "gym", "spa", "hair_care", "beauty_salon"]:
    return "Misc"


MAP_DISTANCE = 160
def distCalc(dist):
  return (MAP_DISTANCE - dist)/MAP_DISTANCE

def wasOutOfState(state):
  return state != 'MD'

def getDistance(lat1, lon1, lat2, lon2):
  # approximate radius of earth in km
  R = 6373.0

  lat1 = radians(lat1)
  lon1 = radians(lon1)
  lat2 = radians(lat2)
  lon2 = radians(lon2)

  dlon = lon2 - lon1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))

  return R * c

def isWeekend(stringDate):
  date = datetime.datetime.strptime(stringDate, "%Y-%m-%dT%H:%M:%S" )
  return date.weekday() >= 5 or (date.weekday() >= 4 and date.hour > 18)

def isHoliday(stringDate):
  us_holidays = holidays.UnitedStates()  # or holidays.US()
  date = datetime.datetime.strptime(stringDate, "%Y-%m-%dT%H:%M:%S" )
  return True if date in us_holidays else False

def cleanData(data):
  returnData = []
  for j in data:
    # remove these keys from the object
    j.pop('HAZMAT', None)
    j.pop('Article', None)
    j.pop('Property Damage', None)
    j.pop('Arrest Type', None)
    j.pop('VehicleType', None)
    j.pop('Charge', None)
    j.pop('Agency', None)
    j.pop('Driver City', None)
    j.pop('Geolocation', None)
    j.pop('Work Zone', None)
    j.pop('Commercial License', None)
    j.pop('Personal Injury', None)
    j.pop('Driver State', None)
    j.pop('SubAgency', None)
    j.pop('Description', None)
    j.pop('DL State', None)
    j.pop('Make', None)
    j.pop('Model', None)
    j.pop('Alcohol', None)
    j.pop('Name', None)

    if ('Year' in j):
      j['Car Year'] = j['Year']
    j.pop('Year', None)

    # get from google maps
    j['Road Type'] = categorizeRoad(j['roadname'])
    j.pop('roadname')

    # time must be in format Y-M-DTH-M-S
    date = datetime.datetime.now()
    j["Time"] = strftime("%Y-%m-%dT%H:%M:%S")
    hour = date.hour
    j['Morning'] = True if  hour >= 4 and hour < 12 else False
    j['Afternoon'] = True if  hour >= 12 and hour < 16 else False
    j['Evening'] = True if  hour >= 16 and hour < 22 else False
    j['Night'] = True if  hour >= 22 or hour < 4 else False

    j['Holiday'] = isHoliday(j["Time"])
    j['Weekend'] = isWeekend(j["Time"])

    for key in j:
      if (j[key] == 'no' or j[key] == 'No'):
        j[key] = False
      elif (j[key] == 'yes' or j[key] == 'Yes'):
        j[key] = True

    avgRating = 0;
    ratingLen = 0;
    index = 0
    while (index < len(j['nearby'])):
      # calc distance between orgin and destination
      j['nearby'][index]['Distance'] = getDistance(float(j['Latitude']), float(j['Longitude']), float(j['nearby'][index]['lat']), float(j['nearby'][index]['lng']))
      log = [];
      if (len(j['nearby'][index]['types']) > 0):
        t = 0
        while(t < len(j['nearby'][index]['types'])):
          c = typeCategories(j['nearby'][index]['types'][t], log)
          if (c is not None):
            log.append(c)
            if(c in j):
              j[c] += 1 *distCalc(j['nearby'][index]['Distance']);
            else:
              j[c] = 1 * distCalc(j['nearby'][index]['Distance']);
          t += 1

      if ('rating' in j['nearby'][index]):
        avgRating += float(j['nearby'][index]['rating'])
        ratingLen += 1;

      index += 1
    if (ratingLen > 0):
      j['AvgRating'] = avgRating / ratingLen

    j.pop("nearby", None)
    returnData.append(j)
  return returnData
  
try:
  data = json.loads(sys.argv[1])
  printObj = {'status': 'OK', "data": []}
  printObj['data'] = cleanData(data);
  print json.dumps(printObj);
except:
  print json.dumps("{'status': 'ERROR', 'data': []}"); 
  sys.exit(1)

