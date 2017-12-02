import json
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.stats import norm

# from picture
OutK = 10
K = 18
dataObj = {'status': 'OK', 'data': {}}
      
def getData():
  inF = open("normalizedData.json", 'r')
  dataObj = {
    'names': [],
    'data': [],
  }
  s = ""
  for l in inF:
    s += l
    if (l.rstrip() == "},"):
      s = s.rstrip()[:-1]
      j = json.loads(s)
      
      j.pop("Violation Type", None)
      j.pop('Time', None)
      j.pop('Latitude', None)
      j.pop('Longitude', None)

      if (not dataObj['names']):
        dataObj['names'] = list(j.keys())

      dataObj['data'].append(list(j.values()))
      s = ""
  inF.close()
  return dataObj

def determineBestK(data, minRange=2, maxRange=-1, step=-1):
  if minRange < 0:
    minRange = 2
  if maxRange < 0:
    maxRange = len(data['names'])
  if maxRange < minRange:
    maxRange = len(data['names'])
    minRange = 2
  yVals = []
  if (step < 0):
    step = int(np.floor((maxRange-minRange)/5))
  for i in range(minRange,maxRange + 1,step):
    kmeans = KMeans(n_init=10, max_iter= 10000, tol=1e-8, verbose=0,
                    n_clusters=i, algorithm="elkan").fit(data['data'])

    avgError = abs(kmeans.score(data['data']))/len(data['data'])

    yVals.append(avgError)
  plt.title('Best K-mean')
  plt.plot(list(range(minRange,maxRange + 1,step)), yVals)
  plt.axis([minRange - .5, maxRange + .5, 0, yVals[0] + .5])
  plt.show()
  
def findOutliers(x, outlierConstant=1.5): # 1.5 is standard
  a = np.array(x)
  upper_quartile = np.percentile(a, 75)
  lower_quartile = np.percentile(a, 25)
  IQR = (upper_quartile - lower_quartile) * outlierConstant
  quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
  indexList = []
  for y in range(len(a.tolist())):
      if (a[y] < quartileSet[0] or a[y] > quartileSet[1]):
          indexList.append(y)
  return indexList

def getKmeansStats(kmeans, data):
  stats = {
    "data": [],
    "dataOutliers": []
  }
  for i in range(len(kmeans.labels_)):
    dist = kmeans.score([data['data'][i]])
    label = str(kmeans.labels_[i])
    stats['data'].append({
      "distance": dist,
      "value": data['data'][i],
      "label": label
    })
  # for each label
  for label in set(kmeans.labels_):
    # find all the data values and map them to their distance values
    distancePerLabel = map(lambda d: d['distance'], filter(lambda f: f['label'] == str(label), stats['data']))
    stats["dataOutliers"] += findOutliers(distancePerLabel)

  return stats

def sepTestTrainData(data, percent=10):
  test = []
  train = []
  for d in data:
    if np.random.randint(low=0,high=percent + 1) == 10:
      test.append(d)
    else:
      train.append(d)
  return [test, train]

def calcScorePercent(score, label, stats, addPer=-.2):
  distancePerLabel = map(lambda d: d['distance'], filter(lambda f: f['label'] == str(label), stats['data']))
  return norm.cdf([score] + distancePerLabel)[0]
    

def getTestData(nameOrder):
  try:
    data = json.loads(sys.argv[1])
    nameIndex = 0
    dataArray = []

    for d in range(len(data)):
      dataArray.append([])
      for n in nameOrder:
        dataArray[d].append(data[d][n])
    return dataArray
  except:
    print json.dumps("{'status': 'ERROR', 'data': []}"); 
    sys.exit(1)

# get the data
###print "Retrieving Data..."
data = getData()
testData = getTestData(data['names'])

# statr init k means
###print "Running Initial K-Means for outlier removal"
kmeans = KMeans(n_init=1, max_iter= 100, tol=1e-4, verbose=0,
               n_clusters=OutK, algorithm="elkan").fit(data['data'])

# get the stats for k means
###print "Getting outliers"
stats = getKmeansStats(kmeans, data)

# remove the outliers
###print "Removing Outliers..."
for out in stats['dataOutliers']:
  del data['data'][out]
###print str(len(stats['dataOutliers'])) + " Outliers Removed"

# run k means again without the outliers
###print "Runing K-means on data"
kmeans = KMeans(n_init=5, max_iter= 10000, tol=1e-8, verbose=0,
               n_clusters=K, algorithm="elkan").fit(data['data'])

###print "Scoring K-Clusters V.S. Your Data"
scores = []
trueScores = []
labels = kmeans.predict(testData)
for t in range(len(testData)):
  label = str(labels[t])
  s = abs(kmeans.score([testData[t]]))
  sp = str(calcScorePercent(s, label, stats))
  scores.append({ "ScoreTrue": s, "ScorePercent": sp, "Label": label})
  trueScores.append(s)
  
dataObj['data']["MinScore"] = str(np.amax(trueScores))
dataObj['data']["MaxScore"] = str(np.amin(trueScores))
dataObj['data']["MeanScore"] = str(np.mean(trueScores))
dataObj['data']["StdDevScore"] = str(np.std(trueScores))
dataObj['data']["AverageScore"] = str(np.average(trueScores))
dataObj['data']["Scores"] = scores

print json.dumps(dataObj)

