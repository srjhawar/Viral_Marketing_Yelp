from __future__ import division
from collections import defaultdict, Iterable
import matplotlib.pyplot
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import collections
import json
import ijson
import sys
import datetime
import operator
import numpy as np
import eigen_centrality
import sklearn.preprocessing
from scipy.stats.stats import pearsonr

# loads user json file and creates dicts for mappings for 
# uid -> id, id -> uid, id -> user's star ratings, id -> user's fan following, id -> review count made by user#
def user_id_mapping():
	user_data = "am-users-filtered.json"
	uid_to_id_dict = {}
	id_to_uid_dict = {}
	index = 1
	with open(user_data,'r') as f:
		for line in f:
			dict_users = json.loads(line)
			userid = dict_users['user_id']
			uid_to_id_dict[userid] = index
			id_to_uid_dict[index] = userid
			uid_fans[index]=int(dict_users['fans'])
			uid_stars[index]=float(dict_users['average_stars'])
			uid_revcnt[index]=int(dict_users['review_count'])
			index += 1
	return uid_to_id_dict, id_to_uid_dict

# this function loads check-in data json in two forms
# 1. business_checkins_dict - this is a dict of business -> user timestamp dict.
# The user timestamp dict maps id -> timestamp of checkin made by user for the business
# 2. user checkins dict - this is a dict of id ->  total number of checkins made by this user for all businesses
def load_checkin_data():
	global all_business_list
	filename = "am-checkin-filtered.json"
	business_checkins = collections.defaultdict(dict)
	user_checkins = {}

	with open(filename,'r') as f:
		for line in f:
			dict_checkins = json.loads(line)
			
			user = dict_checkins['user_id']
			business = dict_checkins['business_id']
			all_business_list.append(business)
			date = dict_checkins['date']
			date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
			id = uid_to_id_dict[user]
			## We want to include only first checkin for a particular restr. for particular user
			if business not in business_checkins:
				business_checkins[business] = {}
			else:
				# Only first time checkin
				if id not in business_checkins[business]:
					business_checkins[business][id] = date

					if id not in user_checkins:
						user_checkins[id] = 1
					else:
						user_checkins[id] += 1

	return user_checkins, business_checkins

# this is phase1 of our algorithm
# main goal of phase 1 is to calculate T_v_to_u
# it is the average time difference between the actions performed by u after v
def phase1(business_list):
	for business in business_list:
		user_timestamp_dict = business_checkins_dict[business]
		## List of tuples of (user,timestamp)
		sorted_checkins = sorted(user_timestamp_dict.items(), key=operator.itemgetter(1))
		current_table = {}
		# look at checkins in ascending chronological order
		for tuple_x in sorted_checkins:
			user = tuple_x[0]
			date = tuple_x[1]
			parents = []
			# find a user's friends
			friends = friend_list[user]
			# we consider only those checkins of friends that are already added to the table
			# if a friend was already added to the current table before a user and he checked in before the user
			# we can then say, that he is a candidate for influencing user and we call it the user's parent
			for friend in current_table:
				if friend in friends:
					u_time = date  ## node getting influenced
					v_time = current_table[friend]  #influencer
					if (v_time < u_time):
						A_v_to_u[friend,user] += 1 
						## to update T
						# T keeps noting the time-difference between the two checkins, and at the end we can find avg. time difference
						if friend in T_numerator:
							if user in T_numerator[friend]:
								T_numerator[friend][user] += u_time - v_time
							else:
								T_numerator[friend][user] = u_time - v_time
						else:
							T_numerator[friend][user] = u_time - v_time
						#we update T_v_to_u to the avg. time difference between all checkins made by v (influencer) and u (influenced)
						T_v_to_u[friend,user] = (T_numerator[friend][user]).days/A_v_to_u[friend,user]
						parents.append(friend)
			current_table[user] = date

# this is phase 2 of our algorithm
# the main aim of this phase is to calculate A_v_to_u and calculate influ(u)
# A_v_to_u can be defined as the number of actions for which v influenced u
# we can then use this A_v_to_u to calculate p_v_to_u
# p_v_to_u = A_v_to_u / A_v 
# where A_v is number of actions performed by v
# before phase2 is called, A_v_to_u is reset
# influ(u) determines how susceptible a user is to be influenced
def phase2(business_list):
	num_of_actions={}
	for business in business_list:
		user_timestamp_dict = business_checkins_dict[business]
		## List of tuples of (user,timestamp)
		sorted_checkins = sorted(user_timestamp_dict.items(), key=operator.itemgetter(1))
		current_table={}
		for tuple1 in sorted_checkins:
			flag=0
			user=tuple1[0]
			date=tuple1[1]
			parents = []
			friends = friend_list[user]
			for friend in current_table:
				if friend in friends:
					u_time = date  ## node getting influenced
					v_time = current_table[friend]  #influencer
					dt=u_time - v_time
					# we make sure we count only those actions, whose time difference is less than the avg. threshold T_v_to_u
					if(0<dt.days and dt.days<T_v_to_u[friend,user]):
						A_v_to_u[friend,user] += 1
						parents.append(friend)
						if flag==0:
							flag=1
			if parents:
				#influ_update
				A_u=users_checkins_dict[user]
				if flag:
					if user not in num_of_actions:
						num_of_actions[user]=1
					else:
						num_of_actions[user]+=1
				# we define influ(u) = number of actions for which we have evidence that user u was influenced/ total number of actions made by u 
				influ[user]=num_of_actions[user]/A_u
			current_table[user] = date
	
# after phase 1 and phase 2 have been called, we now have the ability to determine influencers based on probability
# args : seeders -> number of seeders that are most influential, W_p : weight of probability factor, W_e : weight of eigen centrality factor
# probability factor takes into account checkins data and eigen_centrality factor takes into account the graph structure
def calculate_influencers(seeders, W_p, W_e):
	temp_influence_score = {}
	weighted_influence_score = {}
	# call this function from eigen_centrality.py to give dict of user->eigen_centrality_score
	eigen_centrality_score = eigen_centrality.eigen_centrality(G,seeders)
	seeders_dict = {}
	# calculate the probability factor, we use a dict temp_influence_score 
	# that is addition of all probabilities p_v_to_u for v with u belonging to v's friend list
	for v in range(1,10637):
		if v in friend_list:
			friends = friend_list[v]
			for u in friends:
				if v in users_checkins_dict:
					if v not in temp_influence_score:
						temp_influence_score[v] = 0
					p_v_to_u[v,u] = A_v_to_u[v,u]/users_checkins_dict[v] 	
					temp_influence_score[v] += p_v_to_u[v,u]
				else:
					temp_influence_score[v] = 0
		else:
			temp_influence_score[v] = 0
			
		#for each v we have its eigen_centrality_score
		if v in eigen_centrality_score:
			eigen_score_v = eigen_centrality_score[v]
		else:
			eigen_score_v = 0
		eigen_centrality_score[v] = eigen_score_v

	infl = []
	eigs = []
	for v in range(1,10637):
		infl.append(temp_influence_score[v])
		eigs.append(eigen_centrality_score[v])
		
	# we normalize the two factors we have removed so far in the range 0 to 1, so the weights we use work well
	infl = sklearn.preprocessing.normalize(np.array(infl).reshape(1,-1))[0]
	eigs = sklearn.preprocessing.normalize(np.array(eigs).reshape(1,-1))[0]
	
	# finally, on basis of weights in the args, we calculate weighted_influence_score of each user with both factors into account
	for v in range(1,10637):
		weighted_influence_score[v] = (W_p*infl[v-1]) + (W_e*eigs[v-1])	

	# to find top seeders, we sort this weighted score in reverse order and find the top seeders
	sorted_weighted_influence_score = sorted(weighted_influence_score.items(), key=operator.itemgetter(1), reverse = True)
	sorted_weighted_influence_score = sorted_weighted_influence_score[:seeders+1]
	
	# our function finally returns seeders_dict which maps id -> weighted_influence_score_of_user
	for tuple in sorted_weighted_influence_score:
		user = tuple[0]
		weighted_influence_score_of_user = tuple[1]
		#print "user, weighted, orig, eig : %d, %f, %f, %f, %d" % (user, weighted_influence_score_of_user, temp_influence_score[user],eigen_centrality_score[user], len(friend_list[user]))
		seeders_dict[user] = weighted_influence_score_of_user

	return seeders_dict

# this function determines following reviews for the given data set arg for each user
def evaluate(business_list):
	user_following_count = {}
	for business in business_list:
		user_timestamp_dict = business_checkins_dict[business]
		## List of tuples of (user,timestamp)
		sorted_checkins = sorted(user_timestamp_dict.items(), key=operator.itemgetter(1))
		current_table={}
		for tuple1 in sorted_checkins:
			#print tuple1
			user=tuple1[0]
			date=tuple1[1]
			parents = []
			friends = friend_list[user]
			for friend in current_table:
				if friend in friends:
					u_time = date  ## node getting influenced
					v_time = current_table[friend]  #influencer
					if(v_time < u_time):
						parents.append(friend)
			# note it is important here to notice that we are dividing the credit for the following review equally among all its parents
			# so, if a review was following 2 reviews, the 2 users who made those reviews would receive credit 0.5 and 0.5
			for parent in parents:
				c=1/len(parents)
				if parent in user_following_count:
					user_following_count[parent] += c
				else:
					user_following_count[parent] = c
			current_table[user] = date
		
	return user_following_count

# to find correlation of stars with user_following_count 
# to find correlation of fans with user_following_count
#Since we do not observe strong correlation of the above two factors with user_following_count
#We do not include them to find influencers
def correlation():
	stars_list = []
	fans_list = []
	following_count_list = []
	user_following_count_dict = evaluate(all_business_list)
	for user in user_following_count_dict:
		if user in user_following_count_dict and user in uid_stars and user in uid_fans:
			stars_list.append(uid_stars[user])
			fans_list.append(uid_fans[user])
			following_count_list.append(user_following_count_dict[user])
	print "pearsonr r,p values for stars vs following count"
	print pearsonr(stars_list,following_count_list)
	print "pearsonr r,p values for fans vs following count"
	print pearsonr(fans_list,following_count_list)
	plt.title("fans vs following count")
	#plt.plot(following_count_list,stars_list)
	#plt.savefig("stars_correlation.png")
	#matplotlib.pyplot.scatter(following_count_list,stars_list)
	matplotlib.pyplot.scatter(fans_list,following_count_list)
	matplotlib.pyplot.savefig("fans_followingcount.png")



def evaluate_ground_truth(algorithm_influencer_list):
	tp = 0
	tn = 0
	fp = 0
	fn = 0
	for influencer in algorithm_influencer_list:
		if influencer in ground_truth:
			tp += 1
		else:
			fp += 1

	for influencer in ground_truth:
		if influencer not in algorithm_influencer_list:
			fn +=1
	
	for user in users_checkins_dict:
		if user not in algorithm_influencer_list and user not in ground_truth:
			tn += 1

	precision = tp/(tp + fp)
	recall = tp/(tp+fn)
	accuracy = (tp + tn)/(tp+tn+fp+fn)
	print "precision,recall,accuracy"
	return precision, recall,accuracy




# initialization - A_v_to_u, T_v_to_u and p_v_to_u are initialized as empty 2-D matrices with 0
# we can think of them as adjacency matrices with metric based values for each combination of v and u
A_v_to_u = np.zeros((10637,10637))
T_v_to_u = np.zeros((10637,10637))
p_v_to_u = np.zeros((10637,10637))

# friend_list - dict mapping user to friends
G = nx.read_adjlist("am-filtered.adjlist")
num_nodes = G.number_of_nodes()
friend_list = {}
for i in range(1,num_nodes+1):
	friend_list[i] = [int(j) for j in G.neighbors(str(i))]

# calling user_id_mapping initializes all below structures
uid_fans={}
uid_stars={}
uid_revcnt={}
uid_yelps={}
uid_to_id_dict , id_to_uid_dict= user_id_mapping()

# set of all unique business ids
all_business_list = []
# call load check-in data to initialize our data-structures
users_checkins_dict,business_checkins_dict = load_checkin_data()
all_business_list=list(set(all_business_list))
train_business = all_business_list[:400]
test_business = all_business_list[400:]



# t_numerator is for (v,u) for all businesses
T_numerator = collections.defaultdict(dict)

# call phase1 with training data set
phase1(train_business)

# reinitialize A_v_to_u and influ  and call phase2 with training data set
A_v_to_u = np.zeros((10637,10637))
influ={}
phase2(train_business)

# set number of seeders needed
seed_num = 100

# determine following checkins for each user
user_following_count = evaluate(test_business)

correlation()

# determine the top seeders 
seeders_dict_only_checkins = calculate_influencers(seed_num, 1.0, 0.0)
seeders_dict = calculate_influencers(seed_num, 0.65, 0.35)








