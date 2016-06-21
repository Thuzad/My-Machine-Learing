from numpy import *

def loadDataSet(fileName):
	dataMat = []
	fr = open(fileName)
	for line in fr.readlines():
		curLine = line.strip().split('\t')
		fltLine = map(float, curLine)
		dataMat.append(fltLine)
	return dataMat

def distEclud(vecA, vecB):
	return sqrt(sum(power(vecA - vecB, 2)))

def randCent(dataSet, k):
	n = shape(dataSet)[1]
	centroids = mat(zeros((k ,n)))
	for j in range(n):
		minJ = min(dataSet[:,j])
		rangeJ = float(max(dataSet[:,j]) - minJ)
		centroids[:,j] = mat(minJ + rangeJ * random.rand(k ,1))
	return centroids

def kMeans(dataSet, k, distMeas = distEclud, createCent = randCent):
	m = shape(dataSet)[0]
	clusterAssment = mat(zeros((m ,2)))
	centroids = createCent(dataSet, k)
	clusterChanged = True
	while clusterChanged:
		clusterChanged = False
		for i in range(m):
			minDist = inf; minIndex = -1
			for j in range(k):
				distJI = distMeas(centroids[j,:], dataSet[i,:])
				if distJI < minDist:
					minDist = distJI; minIndex = j
			if clusterAssment[i,0] != minIndex: clusterChanged = True
			clusterAssment[i,:] = minIndex,minDist**2
		#print centroids
		for cent in range(k):
			ptsInClust = dataSet[nonzero(clusterAssment[:,0].A == cent)[0]]
			centroids[cent,:] = mean(ptsInClust, axis = 0)
	return centroids, clusterAssment

def biKmeans(dataSet, k, distMeas = distEclud):
	m = shape(dataSet)[0]
	clusterAssment = mat(zeros((m, 2)))
	centroid0 = mean(dataSet, axis = 0).tolist()[0]
	centList = [centroid0]
	for j in range(m):
		clusterAssment[j, 1] = distMeas(mat(centroid0), dataSet[j,:])**2
	#print "clusterAssment: ", clusterAssment
	while(len(centList) < k):
		lowestSSE = inf
		#print len(centList)
		for i in range(len(centList)):
			ptsInCurrCluster = dataSet[nonzero(clusterAssment[:,0].A == i)[0], :]
			#print "ptsInCurrCluster: ", ptsInCurrCluster
			centroidMat, splitClustAss = kMeans(ptsInCurrCluster, 2, distMeas)
			#print splitClustAss
			sseSplit = sum(splitClustAss[:,1])
			sseNotSplit = sum(clusterAssment[nonzero(clusterAssment[:,0].A != i)[0], 1])
			print "sseSplit, and notSplit: ", sseSplit, sseNotSplit
			if(sseSplit + sseNotSplit) < lowestSSE:
				bestCentToSplit = i
				bestNewCents = centroidMat
				bestClustAss = splitClustAss.copy()
				lowestSSE = sseSplit + sseNotSplit
		bestClustAss[nonzero(bestClustAss[:,0].A == 1)[0], 0] = len(centList)
		bestClustAss[nonzero(bestClustAss[:,0].A == 0)[0], 0] = bestCentToSplit
		print 'the bestCentToSplit is: ', bestCentToSplit
		print 'the len of bestClustAss is: ', len(bestClustAss)
		centList[bestCentToSplit] = bestNewCents[0,:].tolist()[0]
		centList.append(bestNewCents[1,:].tolist()[0])
		clusterAssment[nonzero(clusterAssment[:,0].A == bestCentToSplit)[0],:] = bestClustAss
		#print "clusterAssment: ", clusterAssment
	return mat(centList), clusterAssment

import urllib
import json

def geoGrab(stAddress, city):
	apiStem = 'http://where.yahooapis.com/geocode?'
	params = {}
	params['flags'] = 'J'
	params['appid'] = 'aaa0VN6K'
	params['location'] = '%s %s' % (stAddress, city)
	url_params = urllib.urlencode(params)
	yahooApi = apiStem + url_params
	print yahooApi
	c = urllib.urlopen(yahooApi)
	return json.loads(c.read())

from time import sleep
def massPlaceFind(fileName):
	fw = open('places.txt', 'w')
	for line in open(fileName).readlines():
		line = line.strip()
		lineArr = line.split('\t')
		retDict = geoGrab(lineArr[1], lineArr[2])
		if retDict['ResultSet']['Error'] == 0:
			lat = float(retDict['ResultSet']['Results'][0]['latitude'])
			lng = float(retDict['ResultSet']['Results'][0]['longitude'])
			print "%s\t%f\t%f" % (lineArr[0], lat, lng)
			fw.write('%s\t%f\t%f\n' % (line, lat, lng))
		else: print "error fetching"
		sleep(1)
	fw.close()

def distSLC(vecA, vecB):
	a = sin(vecA[0, 1] * pi / 180) * sin(vecB[0, 1] * pi / 180)
	b = cos(vecA[0, 1] * pi / 180) * cos(vecB[0, 1] * pi / 180) * cos(pi * (vecB[0, 0] - vecA[0, 0]) / 180)
	return arccos(a + b) * 6371.0

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

def clusterClubs(numClust = 5):
	datList = []
	for line in open('places.txt').readlines():
		lineArr = line.split('\t')
		datList.append([float(lineArr[4]), float(lineArr[3])])
	datMat = mat(datList)
	myCentroids, clustAssing = biKmeans(datMat, numClust, distMeas = distSLC)
	fig = plt.figure()
	rect = [0.1, 0.1, 0.8, 0.8]
	scatterMarkers = ['s','o','^','8','p','d','v','h','>','<']
	axprops = dict(xticks = [], yticks = [])
	ax0 = fig.add_axes(rect, label = 'ax0', **axprops)
	imgP = plt.imread('Portland.png')
	ax0.imshow(imgP)
	ax1 = fig.add_axes(rect, label = 'ax1', frameon = False)
	for i in range(numClust):
		ptsInCurrCluster = datMat[nonzero(clustAssing[:,0].A == i)[0],:]
		markerStyle = scatterMarkers[i % len(scatterMarkers)]
		ax1.scatter(ptsInCurrCluster[:,0].flatten().A[0], ptsInCurrCluster[:,1].flatten().A[0], marker = markerStyle, s = 90)
	ax1.scatter(myCentroids[:,0].flatten().A[0], myCentroids[:,1].flatten().A[0], marker = '+', s = 300)
	plt.show()
