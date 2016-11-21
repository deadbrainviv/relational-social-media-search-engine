from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os
import operator

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

list_exceptions = []
list_exceptions.append("md")
list_exceptions.append("mohammad")
list_exceptions.append("mohammed")
list_exceptions.append("khan")
list_exceptions.append("ahmed")
list_exceptions.append("ahmad")
jacc_cutoff = 0.0
seeds_info_file = "all_seeds.txt"

if os.path.isfile(seeds_info_file):
    seeds = {}
    f = open(seeds_info_file, "r")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line:
            token_list = []
            for tt in line.split("===>")[1][1:-1].split(","):
                token_list.append(tt.strip()[1:-1])
            seeds[line.split("===>")[0]] = token_list
    similarities = {}
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        name = person["person"]
        orig_name = person["person"]
        profiles = person["profiles"]
        if len(person["profiles"]) > 0 and person["profiles"][0].has_key("score_jaccard_sim"):
            name = name.lower()
            name = name.replace(".", "")
            tokens_name = name.split()
            for exception in list_exceptions:
                if exception in tokens_name:
                    tokens_name.remove(exception)
            similarities_all_seeds = {}
            for seeds_link, seeds_tokens in seeds.iteritems():
                num = 0.0
                for itr1 in tokens_name:
                    for itr2 in seeds_tokens:
                        if str(itr1) == str(itr2):
                            num = num + 1
                den = 0.0
                temp = []
                for itr1 in tokens_name:
                    temp.append(str(itr1))
                for itr2 in seeds_tokens:
                    temp.append(str(itr2))
                temp = set(temp)
                den = len(temp)
                jacc = num / den
                if jacc > 0.0:
                    similarities_all_seeds[seeds_link] = jacc
            sorted_x = sorted(similarities_all_seeds.items(), key=operator.itemgetter(1), reverse=True)
            similarities[orig_name] = sorted_x
    count = 0
    for similarities_name, similarities_data in similarities.iteritems():
        print "----------------------------", similarities_name, "------------------------------------"
        print similarities_data
        count = count + 1
    print count
else:
    print "No file present!"



































