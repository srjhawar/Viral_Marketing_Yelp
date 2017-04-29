from __future__ import division
from collections import defaultdict, Iterable
import pandas as pd
import networkx as nx
import collections
import json
import ijson
import sys
import datetime
import operator
import numpy as np


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
			index += 1
	return uid_to_id_dict, id_to_uid_dict



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




#print users_checkins_dict
def phase1():
	for business in train_business:
		user_timestamp_dict = business_checkins_dict[business]
		## List of tuples of (user,timestamp)
		sorted_checkins = sorted(user_timestamp_dict.items(), key=operator.itemgetter(1))
		current_table = {}
		for tuple_x in sorted_checkins:
			user = tuple_x[0]
			date = tuple_x[1]
			parents = []
			friends = friend_list[user]
			for friend in current_table:
				if friend in friends:
					u_time = date  ## node getting influenced
					v_time = current_table[friend]  #influencer
					if (v_time < u_time):
						A_v_to_u[friend,user] += 1 
						## to update T
						if friend in T_numerator:
							if user in T_numerator[friend]:
								T_numerator[friend][user] += u_time - v_time
							else:
								T_numerator[friend][user] = u_time - v_time
						else:
							T_numerator[friend][user] = u_time - v_time
						T_v_to_u[friend,user] = (T_numerator[friend][user]).days/A_v_to_u[friend,user]
						parents.append(friend)
			current_table[user] = date


def phase2():
	num_of_actions={}
	for business in train_business:
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
				influ[user]=num_of_actions[user]/A_u
			current_table[user] = date
	

#friend_list - dict mapping user to friends
A_v_to_u = np.zeros((10637,10637))
T_v_to_u = np.zeros((10637,10637))
p_v_to_u = np.zeros((10637,10637))
G = nx.read_adjlist("am-filtered.adjlist")
num_nodes = G.number_of_nodes()
friend_list = {}
for i in range(1,num_nodes+1):
	friend_list[i] = [int(j) for j in G.neighbors(str(i))]
uid_to_id_dict , id_to_uid_dict= user_id_mapping()
all_business_list = []
users_checkins_dict,business_checkins_dict = load_checkin_data()
train_business = all_business_list[:350]
test_business = all_business_list[350:]
user_parents = {}
# t_numerator is for (v,u) for all businesses
T_numerator = collections.defaultdict(dict)

#phase1
phase1()

#phase2
A_v_to_u = np.zeros((10637,10637))
influ={}
phase2()

for v in range(1,10637):
	for u in range(1,10637):
		if v in users_checkins_dict:
			p_v_to_u[v,u] = A_v_to_u[v,u]/users_checkins_dict[v]
		else:
			p_v_to_u[v,u] = 0
		print p_v_to_u[v,u]
