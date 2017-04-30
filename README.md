# Viral_Marketing_Yelp
Capstone project - Viral Marketing with Influence Propogation on Yelp Dataset

Business Problem:
- Identify influencers/trendsetters  in the graph that have the most influence on their friends, i.e. spot those people who create a propagation effect causing their friends to visit a certain place they visit.
- Understand if factors like - average star rating/fans, like count etc make certain users influential 
- Understand how influenceable each user’s consumer choice  is based on his/her social ties

Target Question’s Business Value:
- Once the trendsetters/influencers are identified, they can be targeted by giving incentives. If they are spotted successfully, they can bring in more people to the business (a cascading effect) and hence increase the revenue generated.This is similar to word-of-mouth marketing.
- If a factor is highly correlated to influencing capability, just by looking at the factor value, we can identify if the user could be a candidate for Influencer
- A trend follower with low influenceability might “attenuate” some of the incoming influence from neighbors[1].

Dataset:  We have used dataset from the Yelp Dataset Challenge for Round 9 - http://www.yelp.com/dataset_challenge

Data Preprocessing:
Since the dataset was too huge for us to process on a single machine, we have filtered the dataset to use data only from Las Vegas. We have further extracted only Restaurant businesses from category - American New using MongoDB and Notepad++. To ensure we do not get a sparse graph, we used python package SNAP and found the largest connected component of this graph for our further modeling. 

Data Modeling: 
This can be translated into a social network graph analysis problem 
An undirected graph is constructed with the nodes representing the users and the edges linking each user to their friends
Our algorithms further use the checkin data along with the structure of the graph where each line in the checkin data is a tuple of the form: 
<user_id, business_id, checkin_date>

Dependencies required to run the code:
Packages to be installed:
pandas
networkx
json
ijson
numpy
matplotlib 
sklearn
snap (Download from URL: https://snap.stanford.edu/snappy/#download)
graphviz

Files that should be in the same folder as that of the code:
am-checkin-filtered.json
am-filtered.adjlist
am-users-filtered.json
eigen_centrality.py

Command to run the code:
python viral_marketing.py  

Sample output can be seen in file - final_op.txt

For details - see Readme.pdf
For Preprocessing commands, refer - filter1.py, filter2.py, MongoDBcommands
