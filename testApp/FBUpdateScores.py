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
social_graph_scores_dict = {}
friend_of_verified_person_scores_dict = {}
add_social_and_verified_scores_dict = {}
print "############################## Finding relationships from Social Graph (Starts) ##############################"
for facebook_profile in all_facebook_profiles:
    social_graph_score = 0
    counter_score1 = 0
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        for profile in person["profiles"]:
            if profile.has_key("friends"):
                friends = profile["friends"]
                for friend in friends:
                    if facebook_profile == friend:
                        social_graph_score = social_graph_score + 1
                        social_graph_scores_dict[facebook_profile] = social_graph_score
                    if facebook_profile == friend and profile["actual"] == "yes":
                        counter_score1 = counter_score1 + 1
                        friend_of_verified_person_scores_dict[facebook_profile] = counter_score1
for facebook_profile in all_facebook_profiles:
    score = 0
    if facebook_profile in social_graph_scores_dict.keys():
        score = score + social_graph_scores_dict[facebook_profile]
    if facebook_profile in friend_of_verified_person_scores_dict.keys():
        score = score + friend_of_verified_person_scores_dict[facebook_profile]
        add_social_and_verified_scores_dict[facebook_profile] = score
print "############################## Finding relationships from Social Graph (Ends) ##############################"
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile["profile"] in social_graph_scores_dict.keys():
            profile["score"] = social_graph_scores_dict[profile["profile"]]
        else:
            profile["score"] = 0;
        if profile["profile"] in friend_of_verified_person_scores_dict.keys():
            profile["score1"] = friend_of_verified_person_scores_dict[profile["profile"]]
        else:
            profile["score1"] = 0;
        if profile["profile"] in add_social_and_verified_scores_dict.keys():
            profile["score2"] = add_social_and_verified_scores_dict[profile["profile"]]
        else:
            profile["score2"] = 0;
    person["profiles"] = sorted(person["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
    print person
    # db_client.facebook_db.buet3.update(
    # {"_id": person["_id"]},
    # {
    #     "person": person["person"],
    #     "profiles": person["profiles"]
    # }
    # )
