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


G = nx.read_adjlist("am-filtered.adjlist")
num_nodes = G.number_of_nodes()
friend_list = {}
for i in range(1,num_nodes+1):
	friend_list[i] = [int(j) for j in G.neighbors(str(i))]

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


uid_to_id_dict , id_to_uid_dict= user_id_mapping()
all_business_list = []
users_checkins_dict,business_checkins_dict = load_checkin_data()
train_business = all_business_list[:350]
test_business = all_business_list[350:]
user_parents = {}

A_v_to_u = np.zeros((10637,10637))
T_v_to_u = np.zeros((10637,10637))
p_v_to_u = np.zeros((10637,10637))

## t_numerator is for (v,u) for all businesses
T_numerator = collections.defaultdict(dict)

