from collections import defaultdict, Iterable
import pandas as pd
import networkx as nx
import collections
import json
import ijson
import sys
import snap
fp = open('comp4.txt')
lines = fp.readlines()
com = []
for ln in lines:
	line = ln.strip()
	com.append(int(line))

class Node(object):
    def __init__(self, id, name,user_id, friendlist):
        self.node_id = str(id)
        self.user_id = str(user_id)
        self.friends = friendlist
        self.name = name
        self.checkins = {}

## To return a dict of users which in turn is a dict of business ids and checkin date
def load_checkin_data():
	user_checkins = collections.defaultdict(dict)
	filename = "am-checkin.json"
	dict_checkins = {}
	with open(filename,'r') as f:
		for line in f:
			dict_checkins = json.loads(line)
			
			user = dict_checkins['user_id']
			business = dict_checkins['business_id']
			date = dict_checkins['date']
			user_checkins[user][business] = date
	#print user_checkins[user]

	return user_checkins
'''
def make_node(dict_users, index):
	userid = dict_users["user_id"]
	username = dict_users["name"]
	userfriends = dict_users["friends"]
	user_node = Node(id = index, name = username, user_id = userid, friendlist= userfriends)
	
	return user_node
'''

def building_graph():
	user_data = "am-users.json"
	user_checkins = load_checkin_data()
	node_dict = {}
	user_list=[]
	index = 1
	G = nx.Graph()
	G1 = snap.TUNGraph.New()
	f2 = open('am-users-filtered.json','a+')

	with open(user_data,'r') as f:
		for line in f:
			dict_users = json.loads(line)
			userid = dict_users['user_id']
			username = dict_users['name']
			userfriends = dict_users['friends']
			#print userfriends
			#user_node = Node(id = index, name = username, user_id = userid, friendlist= userfriends)
			#user_node.checkins = user_checkins[user_node.user_id]
			node_dict[userid] = index
			user_list.append(index)
			print index
			if index in com:
				f2.write(line)		
			index += 1

def main():
	#load_checkin_data()
	building_graph()
	

main()










