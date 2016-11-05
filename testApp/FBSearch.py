from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

fbexecute = FBExecute()
colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    print "##############################",person,"##############################"
    for profile in person["profiles"]:
        print profile["profile"], profile["score"], profile["score1"], profile["score2"]

# fbexecute.get_info_about_people("input.txt", colleges, "logins.txt", db_host, db_port, True)
# db_client.facebook_db.buet2.remove({"_id":ObjectId("5817c37d80d62e46dc8f8b59")});
# db_client.drop_database("facebook_db")
# print db_client.database_names()

# Updating score, score1, score2
# all_facebook_profiles = []
# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     for profile in person["profiles"]:
#         all_facebook_profiles.append(profile["profile"])
# all_facebook_profiles = list(set(all_facebook_profiles))
# all_facebook_profiles_score_dict = {}
# all_facebook_profiles_score1_dict = {}
# all_facebook_profiles_score2_dict = {}
# print "############################## Finding relationships from Social Graph (Starts) ##############################"
# for facebook_profile in all_facebook_profiles:
#     counter_score = 0
#     counter_score1 = 0
#     cursor = db_client.facebook_db.buet3.find()
#     for person in cursor:
#         for profile in person["profiles"]:
#             friends = profile["friends"]
#             for friend in friends:
#                 if facebook_profile == friend:
#                     counter_score = counter_score + 1
#                     all_facebook_profiles_score_dict[facebook_profile] = counter_score
#                 if facebook_profile == friend and profile["actual"] == "yes":
#                     counter_score1 = counter_score1 + 1
#                     all_facebook_profiles_score1_dict[facebook_profile] = counter_score1
# for facebook_profile in all_facebook_profiles:
#     score = 0
#     if facebook_profile in all_facebook_profiles_score_dict.keys():
#         score = score + all_facebook_profiles_score_dict[facebook_profile]
#     if facebook_profile in all_facebook_profiles_score1_dict.keys():
#         score = score + all_facebook_profiles_score1_dict[facebook_profile]
#     all_facebook_profiles_score2_dict[facebook_profile] = score
# print "############################## Finding relationships from Social Graph (Ends) ##############################"
# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     for profile in person["profiles"]:
#         if profile["profile"] in all_facebook_profiles_score_dict.keys():
#             profile["score"] = all_facebook_profiles_score_dict[profile["profile"]]
#         else:
#             profile["score"] = 0;
#         if profile["profile"] in all_facebook_profiles_score1_dict.keys():
#             profile["score1"] = all_facebook_profiles_score1_dict[profile["profile"]]
#         else:
#             profile["score1"] = 0;
#         if profile["profile"] in all_facebook_profiles_score2_dict.keys():
#             profile["score2"] = all_facebook_profiles_score2_dict[profile["profile"]]
#         else:
#             profile["score2"] = 0;
#     person["profiles"] = sorted(person["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
#     db_client.facebook_db.buet3.update(
#     {"_id": person["_id"]},
#     {
#         "person": person["person"],
#         "profiles": person["profiles"]
#     }
#     )

# Finding friends of profiles
# flag = False
# browser = fbexecute.login_into_facebook(creds_file="logins.txt")
# for person in cursor:
#     for profile in person["profiles"]:
#         if profile["profile"] == "https://www.facebook.com/mominul.haque.96":
#             flag = True
#         if flag:
#             print " --------------------------------------------------------------------------------------------------"
#             print "Friends analyzed for:", person["person"], "and profile:", profile["profile"]
#             time.sleep(3.0)
#             response = browser.open(profile["profile"] + "/friends")
#             html = response.read()
#             lines = html.split("\n")
#             profile["friends"] = []
#             for line in lines:
#                 if "friends.search" in line:
#                     line1 = line.split("https://www.facebook.com/")
#                     friends = []
#                     for itr in line1:
#                         if not itr.startswith("<div class="):
#                             itr = itr.split("\"")[0]
#                             if "&amp;" in itr:
#                                 itr = itr.split("&amp;")[0]
#                             if "?fref=pb" in itr:
#                                 itr = itr.split("?fref=pb")[0]
#                             if "?ref=br" in itr:
#                                 itr = itr.split("?ref=br")[0]
#                             if itr.endswith("/"):
#                                 itr = itr[:-1]
#                             itr = "https://www.facebook.com/" + itr.strip()
#                             itr = itr.lower()
#                             if not itr.startswith("https://www.facebook.com/pages") and not "university" in itr and not "-" in itr:
#                                 friends.append(itr)
#                     friends = list(set(friends))
#                     profile["friends"] = friends
#                     print "Updating with new data:", profile["friends"]
#                     break
#     if flag:
#         db_client.facebook_db.buet3.update(
#         {"_id": person["_id"]},
#         {
#             "person": person["person"],
#             "profiles": person["profiles"]
#         }
#         )
