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
list_exceptions.append("khan")
list_exceptions.append("ahmed")
list_exceptions.append("ahmad")

jacc_cutoff = 0.525

# while True:
#     if jacc_cutoff > 0.8:
#         break
#
#     jacc_cutoff = jacc_cutoff + 0.1



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

#print dict

similarities = {}
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    name = person["person"]
    profiles = person["profiles"]
    if len(person["profiles"]) == 0:
    # if len(person["profiles"]) == 1 and person["profiles"][0].has_key("jaccard") and person["profiles"][0]["jaccard"] >= 0.0:
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
                if jacc >= jacc_cutoff:
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

#print similarities

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
    final_dict[person] = answers[0]

count = 0
for k, v in final_dict.iteritems():
    print k, v
    count = count + 1
print count

fbexecute = FBExecute()
browser = fbexecute.login_into_facebook(creds_file="logins.txt")
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    if person["person"] in final_dict.keys():
        k = person["person"]
        v = final_dict[k]
        print "---------------------------------------------------------------------"
        print "Person name:", person["person"]
        predicted_profile = v.split(" : ")[0]
        predicted_profile_score = round(float(v.split(" : ")[1].strip()), 3)
        # Building profile starting
        profile = fbexecute.visit_profile(browser, person["person"], predicted_profile)
        profile["jaccard"] = predicted_profile_score
        print profile
        # Building profile done
        person["profile_jaccard_0_dot_525"] = profile
        # db_client.facebook_db.buet3.update(
        # {"_id": person["_id"]},
        # {
        #     "person": person["person"],
        #     "profiles": person["profiles"],
        #     "profile_jaccard_0_dot_2": person["profile_jaccard_0_dot_2"],
        #     "profile_jaccard_0_dot_225": person["profile_jaccard_0_dot_225"],
        #     "profile_jaccard_0_dot_25": person["profile_jaccard_0_dot_25"],
        #     "profile_jaccard_0_dot_275": person["profile_jaccard_0_dot_275"],
        #     "profile_jaccard_0_dot_3": person["profile_jaccard_0_dot_3"],
        #     "profile_jaccard_0_dot_325": person["profile_jaccard_0_dot_325"],
        #     "profile_jaccard_0_dot_35": person["profile_jaccard_0_dot_35"],
        #     "profile_jaccard_0_dot_375": person["profile_jaccard_0_dot_375"],
        #     "profile_jaccard_0_dot_4": person["profile_jaccard_0_dot_4"],
        #     "profile_jaccard_0_dot_425": person["profile_jaccard_0_dot_425"],
        #     "profile_jaccard_0_dot_45": person["profile_jaccard_0_dot_45"],
        #     "profile_jaccard_0_dot_475": person["profile_jaccard_0_dot_475"],
        #     "profile_jaccard_0_dot_5": person["profile_jaccard_0_dot_5"],
        #     "profile_jaccard_0_dot_525": person["profile_jaccard_0_dot_525"]
        #
        #
        # }
        # )































