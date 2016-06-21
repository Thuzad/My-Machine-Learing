def loadDataSet():
	return [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]

def createC1(dataSet):
	C1 = []
	for transaction in dataSet:
		for item in transaction:
			if not [item] in C1:
				C1.append([item])
	C1.sort()
	return map(frozenset, C1)

def scanD(D, Ck, minSupport):
	ssCnt = {}
	for tid in D:
		for can in Ck:
			if can.issubset(tid):
				if not ssCnt.has_key(can): ssCnt[can] = 1
				else: ssCnt[can] += 1
	numItems = float(len(D))
	retList = []
	supportData = {}
	for key in ssCnt:
		support = ssCnt[key] / numItems
		if support >= minSupport:
			retList.insert(0, key)
		supportData[key] = support
	return retList, supportData

def aprioriGen(LK, k):
	retList = []
	lenLK = len(LK)
	for i in range(lenLK):
		for j in range(i + 1, lenLK):
			L1 = list(LK[i])[:k-2]; L2 = list(LK[j])[:k-2]
			L1.sort(); L2.sort()
			if L1 == L2:
				retList.append(LK[i] | LK[j])
	return retList

def qpriori(dataSet, minSupport = 0.5):
	C1 = createC1(dataSet)
	D = map(set, dataSet)
	L1, supportData = scanD(D, C1, minSupport)
	L = [L1]
	k = 2
	while (len(L[k - 2]) > 0):
		Ck = aprioriGen(L[k - 2], k)
		LK, supK = scnaD(D, Ck, minSupport)
		supportData.update(supK)
		L.append(LK)
		k += 1
	return L, supportData
