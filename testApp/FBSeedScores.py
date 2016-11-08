from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

dict = {}

list_exceptions = []
list_exceptions.append("md")
list_exceptions.append("mohammad")
list_exceptions.append("mohammed")

# prepare seeds information
for file in os.listdir(os.getcwd() + "\\seeds\\"):
    data = {}
    filename = os.getcwd() + "\\seeds\\" + file
    content = open(filename, 'r').read()
    lines = content.split("\n")
    for line in lines:
        if line:
            name = line.split("  -  ")[0]
            link = line.split("  -  ")[1]
            name = name.lower()
            name = name.replace(".","")
            tokens = name.split()
            for exception in list_exceptions:
                if exception in tokens:
                    tokens.remove(exception)
            data[link] = tokens
    dict[file] = data

similarities = {}
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    name = person["person"]
    profiles = person["profiles"]
    if len(profiles) == 0:
        name = name.lower()
        name = name.replace(".","")
        tokens_name = name.split()
        for exception in list_exceptions:
            if exception in tokens_name:
                tokens_name.remove(exception)
        for file, data in dict.iteritems():
            for link, tokens_seeds in data.iteritems():
                num = 0.0
                for itr1 in tokens_name:
                    for itr2 in tokens_seeds:
                        if str(itr1) == str(itr2):
                            num = num + 1
                den = 0.0
                temp = []
                for itr1 in tokens_name:
                    temp.append(str(itr1))
                for itr2 in tokens_seeds:
                    temp.append(str(itr2))
                temp = set(temp)
                den = len(temp)
                jacc = num / den
                if jacc > 0.5:
                    if similarities.has_key(name):
                        similarity = similarities[name]
                        if similarity.has_key(file):
                            similarity_file = similarity[file]
                            similarity_file[link] = jacc
                        else:
                            similarity_file = {}
                            similarity_file[link] = jacc
                            similarity[file] = similarity_file
                    else:
                        similarity = {}
                        similarity_file = {}
                        similarity_file[link] = jacc
                        similarity[file] = similarity_file
                        similarities[person["person"]] = similarity

final_dict = {}
for person, similarity in similarities.iteritems():
    answers = []
    for file, similarity_file in similarity.iteritems():
        min = 0.0
        ans = ""
        for link, jacc in similarity_file.iteritems():
            if jacc > min:
                min = jacc
                ans = link
        output = link + " : " + str(min)
        output = output.strip()
        answers.append(output)
    #print person, answers[0]
    final_dict[person] = answers[0]

fbexecute = FBExecute()
browser = fbexecute.login_into_facebook(creds_file="logins.txt")
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    if len(person["profiles"]) == 1 and person["profiles"][0].has_key("jaccard"):
        print person
    # for k, v in final_dict.iteritems():
    #     if k == person["person"]:
    #         print "---------------------------------------------------------------------"
    #         print person
    #         profile = fbexecute.visit_profile(browser, person["person"], v.split(" : ")[0])
    #         profile["jaccard"] = round(float(v.split(" : ")[1].strip()), 3)
    #         person["profiles"].append(profile)
    #         print person
    # db_client.facebook_db.buet3.update(
    # {"_id": person["_id"]},
    # {
    #     "person": person["person"],
    #     "profiles": person["profiles"]
    # }
    # )





















# writing all facebook profiles to disk
# cursor = db_client.facebook_db.buet3.find()
# counter = 0
# for person in cursor:
#     for profile in person["profiles"]:
#         print profile
#         counter = counter + 1
#     # db_client.facebook_db.buet3.update(
#     # {"_id": person["_id"]},
#     # {
#     #     "person": person["person"],
#     #     "profiles": person["profiles"]
#     # }
#     # )
# print "Total number of Facebook profiles:", counter

















