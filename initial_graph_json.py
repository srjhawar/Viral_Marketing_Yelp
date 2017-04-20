from collections import defaultdict, Iterable
import pandas as pd
import networkx as nx
import collections
import json
import ijson
import sys







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
	filename = "yelp_academic_dataset_tip.json"
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
	user_data = "yelp_academic_dataset_user.json"
	user_checkins = load_checkin_data()
	node_dict = {}
	user_list=[]
	index = 1
	G = nx.Graph()
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
			G.add_node(index, name = username, user_id = userid, friendlist = userfriends, checkins = user_checkins[userid])																																																																																																																																																																																																																																																																																			 			if index > 50000:
			if index > 50000:	
				break
			index += 1


	
	#G.add_nodes_from(user_list)
	#print G.number_of_nodes()
	#print user_node.friends
	adj_list = []
	for user in G.nodes():																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																									
		for frnd in G.node[user]['friendlist']:
			if frnd in node_dict:
				temp = (user,node_dict[frnd])
				if (node_dict[frnd],user) not in adj_list:
					print "adding edge"
					adj_list.append(temp)
	G.add_edges_from(adj_list)
	nx.write_adjlist(G,"test.adjlist")
	

def main():
	#load_checkin_data()
	building_graph()
	

main()









