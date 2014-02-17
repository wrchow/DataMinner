# -*- coding:utf-8 -*-
'''
from 2014-02-16

summary:
使用pearson距离来实现基于用户的协同过滤，
pearson距离就是直线的相关系数，协方差/标准差之积，
对于未评分的物品，用用户对物品的平均打分来代替，
因此非公共评分物品打分为0，从而对分子为0的交叉项，可以不做计算，
可以考虑用倒排表，将原本复杂度为O(M)的两个向量相关系数计算，
降低为O(K)，其中M为物品总数，K为公共评分物品总数，
由于评分比较稀疏，因此可以带来，稀疏度的倒数的效率提升；

algorithm:
1. 导入数据，得到M行物品，N列用户的，评分矩阵 ratingsMatrix；
2. 计算用户相似度矩阵 userSimMatrix: （算法复杂度O(N*N)）
	2.1 每个用户对物品的评分均值，
	2.2 利用倒排表，求用户之间的物品交集，
	2.3 计算用户之间的pearson距离，
	2.4 得到用户相似度矩阵，并保存到本地；
3. 得到每个用户的物品推荐列表 recMatrix:
	3.1 排序，TopN可以考虑用最大堆；
	3.2 算法复杂度？
'''

from math import sqrt
from operator import itemgetter

# 1
def load_data(data_path):

	users_items = {}
	#itemSet = set()
	for line in open(data_path):
		try:
		#	print line
			(userId, itemId, rating, timestamp) = line.strip().split('\t')
			users_items.setdefault(userId, {})
			users_items[userId][itemId] = float(rating)
			#itemSet.add(itemId)
		except:
			print 'load data error in split by \\t'

	return users_items#, itemSet

# 2
def calCoItems(users_items):
	
	uCoItemsMat = {}

	itemUsers = {}
	for userId in users_items.keys():
		for itemId in users_items[userId].keys():
			if itemId not in itemUsers.keys():
				itemUsers.setdefault(itemId, [])
			itemUsers[itemId].append(userId)

	for movie, users in itemUsers.items():
		for u1 in users:
			uCoItemsMat.setdefault(u1, {})
			for u2 in users:
				if u1 == u2:
					continue
				uCoItemsMat[u1].setdefault(u2,[])
				uCoItemsMat[u1][u2].append(movie)  	    	

	return uCoItemsMat 

def average_urating(userId, users_items):
	
	average = 0
	
	for itemId in users_items[userId].keys():
		average += users_items[userId][itemId]

	return average * 1.0 / len(users_items[userId])

'''
pearson = part1 / part2
X = P_t_i - A_i
Y = P_t_j - A_j
part1 = sum(X * Y)
part2 = sqrt( sum(X**2) ) * sqrt( sum(Y**2) )
part21 = sum(X**2)
part22 = sum(Y**2)
'''
def calUserSimMatrix(users_items):
	
	uSimMat = {}
	
	uCoItemsMat = calCoItems(users_items)
	#print 'len of uCoItemsMat %d' % len(uCoItemsMat)
	#print uCoItemsMat['40']['48']
 
	for u_i in uCoItemsMat.keys():
		uSimMat.setdefault(u_i, {})
		for u_j in uCoItemsMat[u_i].keys():
			A_i = average_urating(u_i, users_items)
			A_j = average_urating(u_j, users_items)
			part1 = 0
			part21 = 0
			part22 = 0
			for t in uCoItemsMat[u_i][u_j]:
				X = users_items[u_i][t] - A_i
				Y = users_items[u_j][t] - A_j
				part1 += X * Y 	   
				part21 += X**2
				part22 += Y**2
			
			if part21 == 0:
				part21 = 1e-9
			if part22 == 0:
				part22 = 1e-9		
			pearson = part1 * 1.0 / (sqrt(part21) * sqrt(part22)) 
			uSimMat[u_i][u_j] = pearson

	#print 'len of uSimMat %d' % len(uSimMat)
	return uSimMat 
	
# 3
'''
for K similar users each item t's score:
Rec_i_t = part1 / part2
part1 = sum_K( (P_t_j - A_j) * S_i_j )
part2 = sum_K(S_i_j)
'''
from operator import itemgetter
def calRecMatrix(users_items, uSimMat, K):
	
	recMat = {}

	for user_i in users_items.keys():
		recMat.setdefault(user_i, {})
		A_i = average_urating(user_i, users_items)
		part2 = 0.0
		for user_j, S_i_j in sorted(uSimMat[user_i].items(), key=itemgetter(1), reverse=True)[0:K]:
			part2 += S_i_j
			A_j = average_urating(user_j, users_items)
			for item_t, p_t_j in users_items[user_j].items():
				if item_t in users_items[user_i].keys():
					continue 
				if item_t not in recMat[user_i].keys():
					recMat[user_i].setdefault(item_t, 0.0)
				recMat[user_i][item_t] += (p_t_j - A_j) * S_i_j	
		
		for item_t, rating in recMat[user_i].items():
			recMat[user_i][item_t] = A_i + rating / part2	
		
		recMat[user_i] = sorted(recMat[user_i].items(), key=itemgetter(1), reverse=True)	
	
	return recMat




import time
import pickle
import sys

def test1(datapath):
	users_items = load_data(datapath)
	
	print 'cal user similarity matrix begin at %s' % time.ctime()
	simMat = calUserSimMatrix(users_items)
	print 'finish user similarity matrix at %s' % time.ctime()
	sim_output = open(datapath + '.simMat', 'wb')
	pickle.dump(simMat, sim_output)
	sim_output.close()

	print 'cal user recommend matrix begin at %s' % time.ctime()
	recMat =  calRecMatrix(users_items, simMat, 20)
	print 'finish user recommend matrix at %s' % time.ctime()
	rec_output = open(datapath + '.recMat', 'wb')
	pickle.dump(recMat, rec_output)
	rec_output.close()

	print 'rec for user id 182:'
	print recMat['182'][0:20]


# user movielens-100k u_i.base adn u_i.test
def evalue_model(datapath, M):
	for i in range(1, M + 1):
		# training
		fname = 'u' + str(i) + '.base'
		print 'training file of %s' % datapath + fname
		users_items = load_data(datapath + fname)
		#print len(users_items)
		simMat = calUserSimMatrix(users_items)
		sim_output = open(datapath + fname + '.simMat', 'wb')
		pickle.dump(simMat, sim_output)
		sim_output.close()
		# testing
		#fname = 'u' + str(i) + '.test'
		#print 'test file of %s' % fname
		#error:	users_items = load_data(datapath + fname)
		recMat = calRecMatrix(users_items, simMat, 20)
		rec_output = open(datapath + fname + '.recMat', 'wb')
		pickle.dump(recMat, rec_output)
		rec_output.close()
		

if __name__ == '__main__':
	
	if len(sys.argv) < 2:
		print 'Usage: python usercf datapath'
		sys.exit(-1)

	datapath = sys.argv[1]
	#test1()
	evalue_model(datapath, 1)
	
