from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

cursor = db_client.facebook_db.buet3.find()

c = 0
file = open("C:\\Users\\IndervirSingh\\Downloads\\thesis project\\gazi_friend_list.csv", "r")
#file1 = open("C:\\Users\\IndervirSingh\\Documents\\GitHub\\profiling\\testApp\\all_seeds_U.txt", "a")
#file1.write("\n")
for line in file.readlines():
    if "&sk=about" in line:
        c = c + 1
        list_str = line.split(",")[1]
        list_str = list_str.lower()
        list = list_str.split()
        write = line.split("&sk=about")[0] + "===>" + str(list)
        #print write
        #file1.write(write + "\n")
    elif "/about" in line:
        c = c + 1
        list_str = line.split(",")[1]
        list_str = list_str.lower()
        list = list_str.split()
        write = line.split("/about")[0] + "===>" + str(list)
        #print write
        #file1.write(write + "\n")
#print c










# from FBExecute import *
# from FBDb import *
# from bson import ObjectId
# import urllib
# from operator import itemgetter
# import os
#
# db_host = "localhost"
# db_port = 27017
# db_client = FBDb.connect(db_host, db_port)
# cursor = db_client.facebook_db.buet3.find()
#
# file = open("C:\\Users\\IndervirSingh\\Documents\\GitHub\\profiling\\testApp\\all_seeds.txt", "r")
#
# list = []
# for line in file.readlines():
#     list.append(line)
#
# dict = {}
# for ele in list:
#     if dict.has_key(ele):
#         dict[ele] = dict[ele] + 1
#     else:
#         dict[ele] = 1
#
# count_list = 0
# for ele in list:
#     print ele
#     count_list = count_list + 1
#
# count_dict = 0
# for k, v in dict.iteritems():
#     k = k.strip()
#     print k
#     count_dict = count_dict + 1
#
# count_sk = 0
# for ele in list:
#     if "&sk=about" in ele:
#         count_sk = count_sk + 1
# print count_sk










# for person in cursor:
#     print "############################################################"
#     print person["person"]
#     for profile in person["profiles"]:
#         #print profile
#         if profile.has_key("newscore"):
#             print profile["profile"], " === ", profile["newscore"]
#         if profile.has_key("score_jaccard_sim"):
#             print profile["profile"], " --- ", profile["score_jaccard_sim"]
#         if (not profile.has_key("newscore")) and (not profile.has_key("score_jaccard_sim")):
#             print profile["profile"], " --- ", "zero"








