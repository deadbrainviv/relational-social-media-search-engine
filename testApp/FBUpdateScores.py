from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

all_facebook_profiles = []
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        all_facebook_profiles.append(profile["profile"])
all_facebook_profiles = list(set(all_facebook_profiles))
all_facebook_profiles_score_dict = {}
all_facebook_profiles_score1_dict = {}
all_facebook_profiles_score2_dict = {}
print "############################## Finding relationships from Social Graph (Starts) ##############################"
for facebook_profile in all_facebook_profiles:
    counter_score = 0
    counter_score1 = 0
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        for profile in person["profiles"]:
            friends = profile["friends"]
            for friend in friends:
                if facebook_profile == friend:
                    counter_score = counter_score + 1
                    all_facebook_profiles_score_dict[facebook_profile] = counter_score
                if facebook_profile == friend and profile["actual"] == "yes":
                    counter_score1 = counter_score1 + 1
                    all_facebook_profiles_score1_dict[facebook_profile] = counter_score1
for facebook_profile in all_facebook_profiles:
    score = 0
    if facebook_profile in all_facebook_profiles_score_dict.keys():
        score = score + all_facebook_profiles_score_dict[facebook_profile]
    if facebook_profile in all_facebook_profiles_score1_dict.keys():
        score = score + all_facebook_profiles_score1_dict[facebook_profile]
    all_facebook_profiles_score2_dict[facebook_profile] = score
print "############################## Finding relationships from Social Graph (Ends) ##############################"
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile["profile"] in all_facebook_profiles_score_dict.keys():
            profile["score"] = all_facebook_profiles_score_dict[profile["profile"]]
        else:
            profile["score"] = 0;
        if profile["profile"] in all_facebook_profiles_score1_dict.keys():
            profile["score1"] = all_facebook_profiles_score1_dict[profile["profile"]]
        else:
            profile["score1"] = 0;
        if profile["profile"] in all_facebook_profiles_score2_dict.keys():
            profile["score2"] = all_facebook_profiles_score2_dict[profile["profile"]]
        else:
            profile["score2"] = 0;
    person["profiles"] = sorted(person["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
    db_client.facebook_db.buet3.update(
    {"_id": person["_id"]},
    {
        "person": person["person"],
        "profiles": person["profiles"]
    }
    )
