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
##In graph theory, eigenvector centrality (also called eigencentrality) is a measure of the influence of a 
#node in a network. It assigns relative scores to all nodes in the network based on the concept that connections
# to high-scoring nodes contribute more to the score of the node in question than equal connections to low-scoring nodes.

def eigen_centrality(G,seeders):
	
	eigen_centrality_dict= {}
	centrality = nx.eigenvector_centrality(G)
	sorted_eigen_centrality = sorted(centrality.items(), key=operator.itemgetter(1), reverse = True)
	#sorted_eigen_centrality = sorted_eigen_centrality[:seeders+1]
	for tuple in sorted_eigen_centrality:
		user = int(tuple[0])
		eigen_score = tuple[1]
		eigen_centrality_dict[user] = eigen_score
	return eigen_centrality_dict
	

G = nx.read_adjlist("am-filtered.adjlist")
dict = eigen_centrality(G,20)


'''
pr = nx.pagerank(G, alpha=0.9)
print type(pr)

sorted_pagerank= sorted(pr.items(), key=operator.itemgetter(1), reverse = True)
print sorted_pagerank[:10]

print "With Core-S algo"
## K core
# Given a graph G and an integer K, K-cores of the graph 
# are connected components that are left after all vertices of degree less than k have been removed
k_core_graph = nx.k_core(G)
centrality = nx.eigenvector_centrality(k_core_graph)
#print(['%s %0.2f'%(node,centrality[node]) for node in centrality])

sorted_eigen_centrality = sorted(centrality.items(), key=operator.itemgetter(1), reverse = True)
print sorted_eigen_centrality[:10]

'''
