import json
import re
import sys
import webcolors
import datetime

def zeroToOne(val, mini, maxi):
  if val < mini:
    return 0
  if val > maxi:
    return 1
  return (float(val) - mini)/(maxi - mini)

def timesToOneKey(j):
  if (j['Morning'] == True):
    j['TimeClassify'] = 0.0
  elif (j['Afternoon'] == True):
    j['TimeClassify'] = 1.0/3.0
  elif(j['Evening'] == True):
    j['TimeClassify'] = 2.0/3.0
  elif (j['Night'] == True):
    j['TimeClassify'] = 1.0
  j.pop('Night')
  j.pop('Evening')
  j.pop('Afternoon')
  j.pop('Morning')
  
def trueFalseNorm(j):
  for k in j:
    if (j[k] == True or j[k] == "true"):
      j[k] = 1
    elif (j[k] == False or j[k] == "false"):
      j[k] = 0
      

types = ["Political", "Transit", "Doctor", "Food", "Store", "Profession", "Trade", "Institution", "Place_of_worship", "Undesirable", "Attraction", "Misc"]
typesMinMaxObj = {}
racesMap = {
  "WHITE": 0,
  "ASIAN": 0.2,
  "BLACK": 0.4,
  "HISPANIC": 0.6,
  "OTHER": 0.8,
  "NATIVE AMERICAN": 1
}

maxHexColor = int("ffffff", 16)
minHexColor = 0 

roadTypeMap = {
  "Road": 0,
  "Highway": 1
}

genderMap = {
  "F": 1,
  "U": 0.5,
  "M": 0
}

violationMap = {
  "Warning": 0,
  "ESERO": 0,
  "Citation": 1
}

maxHexColor = int("ffffff", 16)
minHexColor = 0 

avgObj = json.load(open("averageData.json"));

def normalize(data):
  returnObj = []
  for j in data:    
    j['Race'] = racesMap[str(j['Race']).upper()]
    j['Color'] = zeroToOne(int(j['Car Color'], 16), minHexColor, maxHexColor)
    j.pop('Car Color')
    j['Gender'] = genderMap[j['Gender']]
    j['Road Type'] = roadTypeMap[j['Road Type']]
    timesToOneKey(j)
    
    trueFalseNorm(j)
    
    if ('Car Year' in j and j['Car Year'] != "" and float(j['Car Year']) > 1900 and float(j['Car Year']) < 2020):
      j['Car Year'] = zeroToOne(j['Car Year'], avgObj['minCarYear'], avgObj['maxCarYear'])
    else:
      j['Car Year'] = avgObj["Average Car Year"]
      
    j.pop('Belts', None)
    
    if ('AvgRating' not in j):
      j['AvgRating'] = avgObj['Average Rating']
    else:
      j['AvgRating'] = zeroToOne(j['AvgRating'], 0, avgObj['maxRating'])
    
    for t in range(len(types)):
      if types[t] in j:
        j[types[t]] = zeroToOne(j[types[t]], avgObj['TypesMinMax'][types[t]]['min'], avgObj['TypesMinMax'][types[t]]['max'])
      else:
        j[types[t]] = 0
    returnObj.append(j)
  return returnObj

try:
  data = json.loads(sys.argv[1])
  printObj = {'status': 'OK', "data": []}
  printObj['data'] = normalize(data);
  print json.dumps(printObj);
except:
  print json.dumps("{'status': 'ERROR', 'data': []}"); 
  sys.exit(1)
      
