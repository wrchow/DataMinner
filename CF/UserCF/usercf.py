# -*- coding:utf-8 -*-
'''
单机版本的usercf算法:
1. 输入打分数组，如movielens数据的ratings.dat，格式为<userid,movieid,pref>；
2. 构建用户向量，物品向量，从而得到打分N*M的矩阵；
3. 给出距离函数，并计算用户相似度矩阵，算法复杂度为O(N^2*M);
4. 对算法进行优化；
5. 根据用户相似度矩阵，进行TopN推荐；
'''

import time
import sys
from operator import itemgetter, attrgetter
from math import sqrt

# user id | item id | rating | timestamp
data_path = '../../data/movielens/ml-100k/u.data'

if len(sys.argv) < 2:
	print 'Usage: usercf.py datapath'
else:
	data_path = sys.argv[1]

# create N*M ratings matrix by ratings.dat
def load_data():
	ratings_matrix = {}
	itemSet = set()	
	userSet = set()
	for line in open(data_path):
		(userId, itemId, rating, timestamp) = line.strip().split('\t')	
		ratings_matrix.setdefault(userId,{})
		ratings_matrix[userId][itemId] = float(rating)
		itemSet.add(itemId)
		userSet.add(userId)

	return ratings_matrix, itemSet, userSet  

# distance functions

# 1. Euclidean distance   d = 1 / (1 + dist)
def euclidean_dist(u1, u2):
	dist = 0.0
	for itemId1 in u1.keys():
		for itemId2 in u2.keys():
			if itemId1 == itemId2:
				dist += (u1[itemId1] - u2[itemId2])**2

	return 1.0 / (1.0 + sqrt(dist))



# calculate the user simmilarity matrix
def user_sim(ratings_matrix):
	userSim = {}
	for userId1 in ratings_matrix.keys():
		for userId2 in ratings_matrix.keys():
			if userId1 != userId2:
				userSim.setdefault(userId1, {})
				u1 = ratings_matrix[userId1]
				u2 = ratings_matrix[userId2]
				userSim[userId1][userId2] = euclidean_dist(u1, u2)

	return userSim
	

# get top N rec items
def calRecMatrix(ratings_matrix, items, userSim):
	recMatrix = {}
	for userId_k in userSim.keys():
		Score_ij = 0.0
		for itemId_i in items:
			if itemId_i in ratings_matrix[userId_k]:
				continue
			for sim_user_j in userSim[userId_k]:
				Score_ij += ratings_matrix[itemId_i][sim_user_j] * userSim[userId_k][sim_user_j]
			recMatrix.setdefault(userId_k, {}) 
			recMatrix[userId_k][itemId_i] = Score_ij

	return recMatrix

def getRec(recMatrix, user, N):
	rec_v = recMatrix[user]
	pred = sorted(rec_v.items(), key=itemgetter(1), reverse=True)[0:N]
	return pred 

import pickle
if __name__ == "__main__":
	
	ratings_matrix, itemSet, userSet  = load_data()
	print 'import len of %d users\' data from %s' % (len(ratings_matrix), data_path)
	
	u1 = ratings_matrix[ratings_matrix.keys()[0]]
	u2 = ratings_matrix[ratings_matrix.keys()[1]]
	d12 = euclidean_dist(u1, u2)
	print 'euclidean dist of u1 and u2 is %f' % d12 
	
	print 'calculate the user simmilarity matrix from %s' % time.ctime()
	userSim = user_sim(ratings_matrix)
	print 'finish user sim matrix of len %d at %s' % (len(userSim), time.ctime())
	sim_output = open('Movielens.UserSim.1m', 'wb')
	pickle.dump(userSim, sim_output)
	sim_output.close()	

	print 'calculate the rec matrix from %s' % time.ctime()
	recMatrix =	calRecMatrix(ratings_matrix, itemSet, userSim)
	print 'finish the rec matrix at %s' % time.ctime()
	rec_output = open('Movielens.Recs.1m', 'wb')
	pickle.dum(recMatrix, rec_output)
	rec_output.close()

	print 'rec for user 182:'
	print getRec(recMatrix, '182', 20)
			
