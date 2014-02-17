# -*- coding:utf-8 -*-
'''
from 20140216

summary:
1. 计算准确率，召回率，覆盖率，流行度等指标；

algorithm:

'''

'''
P = sum(R_u && T_u) / sum(R_u)
P = part1 / part2
'''
def calPrecision(recMat, testMat):
	part1 = 0
	part2 = 0
	for u in recMat.keys():
		for (i,rating) in recMat[u]:
			if testMat.has_key(u) and i in testMat[u]:
				part1 += 1
			part2 += 1

	if part2 > 0:
		return part1 * 1.0 / part2
	else:
		return 0.0

def load_data(dataPathName):
	
	dataMat = {}
	
	for line in open(dataPathName, 'rb'):
		(userId, itemId, rating, timestamp) = line.strip().split('\t')
		dataMat.setdefault(userId, {})
		dataMat[userId][itemId] = float(rating)

	return dataMat	 	

import pickle
def evalue(datapath, M):
	prec = 0.0
	for i in range(1, M+1):
		fname = 'u' + str(i) + '.base.recMat'
		rec_input = open(datapath + fname, 'rb')
		recMat = pickle.load(rec_input)
		rec_input.close()
		testMat = load_data(datapath + 'u' + str(i) + '.test')
		#print testMat
		p = calPrecision(recMat, testMat)
		prec += p
		print 'precison of u%d is %f.' % (i, p)
	print 'precison of M%d is %f.' % (M, prec/M) 

import sys
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'Usage: python datapath'
	datapath = sys.argv[1]
	evalue(datapath, 5)
		

	
	
