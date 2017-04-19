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

def make_node(dict_users, index):
	userid = dict_users["user_id"]
	username = dict_users["name"]
	userfriends = dict_users["friends"]
	user_node = Node(id = index, name = username, user_id = userid, friendlist= userfriends)
	
	return user_node


def building_graph():
	user_data = "yelp_academic_dataset_user.json"
	user_checkins = load_checkin_data()
	node_dict = {}
	node_list=[]
	index = 1
	with open(user_data,'r') as f:
		objects = ijson.items(f,'yelp_academic_dataset_user.item')
		for o in objects:
			print o
		sys.exit(1)
		for prefix,event,value in parser:
			if prefix == 'user_id':
				userid = value
			if prefix == 'name':
				username = value
			if prefix == 'friends':
				userfriends = value
			user_node = Node(id = index, name = username, user_id = userid, friendlist= userfriends)
			user_node.checkins = user_checkins[user_node.user_id]
			node_dict[index] = user_node
			node_list.append(index)
			print index
			index += 1


	G = nx.Graph()
	G.add_nodes_from(node_list)
	print G.number_of_nodes()

def main():
	#load_checkin_data()
	building_graph()
	

main()









