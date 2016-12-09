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
        status = False
        for profile in profiles:
            if profile["actual"] == "yes":
                status = True
        #if len(person["profiles"]) > 0 and person["profiles"][0].has_key("score_jaccard_sim"):
        if status == False:
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

    fb_profiles_dict = {}
    for similarities_name, similarities_data in similarities.iteritems():
        #print "----------------------------", similarities_name, "------------------------------------"
        for itr in similarities_data:
            #print itr
            if fb_profiles_dict.has_key(similarities_name):
                fb_profiles_dict[similarities_name].append(itr)
            else:
                list = []
                list.append(itr)
                fb_profiles_dict[similarities_name] = list

    for k,v in fb_profiles_dict.iteritems():
        print k,":",v
    print "Size of dict:", len(fb_profiles_dict)

    all_fb_profiles = {}
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        for profile in person["profiles"]:
            all_fb_profiles[profile["profile"]] = profile

    fb = FBExecute()
    browser = fb.login_into_facebook(creds_file="logins.txt")
    cursor = db_client.facebook_db.buet3.find()

    count = 0
    for person in cursor:
        is_verified = False
        for profile in person["profiles"]:
            if profile["actual"] == "yes":
                is_verified = False
                break
        if not is_verified:
            print "-------------------------",person["person"],"-------------------------"
            profile_urls_dict = {}
            print "Total dict size", len(fb_profiles_dict)
            if fb_profiles_dict.has_key(person["person"]):
                for profile in fb_profiles_dict[person["person"]]:
                    profile_urls_dict[profile[0]] = profile[1]
            print "How much we need to see", len(profile_urls_dict)
            for k,v in profile_urls_dict.iteritems():
                print k,v
                profile = {}
                if all_fb_profiles.has_key(k):
                    profile = all_fb_profiles[k]
                else:
                    profile = fb.visit_profile(browser, k)
                    all_fb_profiles[profile["profile"]] = profile
                profile["newscore"] = v
                person["profiles"].append(profile)
            db_client.facebook_db.buet3.update(
                {"_id": person["_id"]},
                {
                    "person": person["person"],
                    "profiles": person["profiles"]
                }
            )
        count = count + 1
        print count, "done!"
else:
    print "No file present!"



































