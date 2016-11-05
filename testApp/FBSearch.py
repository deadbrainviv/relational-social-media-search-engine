from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

fbexecute = FBExecute()
colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

# fbexecute.get_info_about_people("input.txt", colleges, "logins.txt", db_host, db_port, True)
# db_client.facebook_db.buet2.remove({"_id":ObjectId("5817c37d80d62e46dc8f8b59")});

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    print "############",person["person"],"############"
    for profile in person["profiles"]:
        print profile["profile"]," - ",profile["score"]








# Sorting the scores
# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     person["profiles"] = sorted(person["profiles"], key=lambda k: k["score"], reverse=True)
#     db_client.facebook_db.buet3.update(
#     {"_id": person["_id"]},
#     {
#         "person": person["person"],
#         "profiles": person["profiles"]
#     }
#     )

# Updating scores of all the profiles
# all_facebook_profiles = []
# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     for profile in person["profiles"]:
#         #print profile
#         all_facebook_profiles.append(profile["profile"])
# counter = 0
# all_facebook_profiles_score_dict = {}
# print "############################## Finding relationships from Social Graph (Starts) ##############################"
# for facebook_profile in all_facebook_profiles:
#     counter_local = 0
#     cursor = db_client.facebook_db.buet3.find()
#     for person in cursor:
#         for profile in person["profiles"]:
#             friends = profile["friends"]
#             for friend in friends:
#                 if facebook_profile == friend:
#                     counter = counter + 1
#                     counter_local = counter_local + 1
#                     all_facebook_profiles_score_dict[facebook_profile] = counter_local
#                     print facebook_profile, "found in friend list of ", profile["profile"]
# print "Total:", counter, "relationships found!"
# print "Going to iterate score map:"
# for k,v in all_facebook_profiles_score_dict.items():
#     print k, " - ", v
# print "Done iterating the score map!"
# print "############################## Finding relationships from Social Graph (Ends) ##############################"
# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     for profile in person["profiles"]:
#         if profile["profile"] in all_facebook_profiles_score_dict.keys():
#             profile["score"] = all_facebook_profiles_score_dict[profile["profile"]]
#         else:
#             profile["score"] = 0;
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
