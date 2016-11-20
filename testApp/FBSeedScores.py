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
fbx = FBExecute()
browser = fbx.login_into_facebook(creds_file="logins.txt")

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
        if len(person["profiles"]) == 0:
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
    # for similarities_name, similarities_data in similarities.iteritems():
    #     print "################################", similarities_name, "########################################"
    #     print similarities_data
    count = 0
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        name = person["person"]
        print "-----------------------------------------------------------------------"
        if name in similarities.keys():
            profiles = []
            for link_jacc in similarities[name]:
                profile = fbx.visit_profile(browser, name, link_jacc[0])
                profile["score_jaccard_sim"] = link_jacc[1]
                print link_jacc[0], link_jacc[1]
                profiles.append(profile)
            count = count + 1
            print count
            person["profiles"] = profiles
            # db_client.facebook_db.buet3.update(
            #     {"_id": person["_id"]},
            #     {
            #         "person": person["person"],
            #         "profiles": person["profiles"],
            #     }
            # )
    print count

else:
    seeds = {}
    seed_folder_dir = os.listdir(os.getcwd() + "\\seeds\\")
    for file in seed_folder_dir:
        filename = os.getcwd() + "\\seeds\\" + file
        content = open(filename, 'r').read()
        lines = content.split("\n")
        for line in lines:
            if line:
                name = line.split("  -  ")[0]
                link = line.split("  -  ")[1]
                name = name.lower()
                name = name.replace(".", "")
                tokens = name.split()
                for exception in list_exceptions:
                    if exception in tokens:
                        tokens.remove(exception)
                if link in seeds.keys():
                    union_prev_and_curr = list(set().union(seeds[link], tokens))
                    seeds[link] = union_prev_and_curr
                else:
                    fbx_name = fbx.get_profile_name(browser, link)
                    fbx_name = fbx_name.lower()
                    fbx_name = fbx_name.replace(".", "")
                    facebook_tokens = fbx_name.split()
                    print facebook_tokens
                    seeds[link] = list(set().union(tokens, facebook_tokens))
    f = open(seeds_info_file, "w")
    for k, v in seeds.iteritems():
        f.write(str(k) + "===>" + str(v) + "\n")
    f.close()



































