from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

cursor = db_client.facebook_db.buet3.find()

count = 0
count1 = 0
count2 = 0
count3 = 0
count4 = 0
count5 = 0
count6 = 0
count7 = 0
count8 = 0
count9 = 0
count10 = 0
count11 = 0
count12 = 0
count13 = 0
zero = 0
for person in cursor:
    if len(person["profiles"]) == 0:
        zero = zero + 1
    if person.has_key("profile_jaccard_0_dot_2"):
        count = count + 1
    if person.has_key("profile_jaccard_0_dot_225"):
        count1 = count1 + 1
    if person.has_key("profile_jaccard_0_dot_25"):
        count2 = count2 + 1
    if person.has_key("profile_jaccard_0_dot_275"):
        count3 = count3 + 1
    if person.has_key("profile_jaccard_0_dot_3"):
        count4 = count4 + 1
    if person.has_key("profile_jaccard_0_dot_325"):
        count5 = count5 + 1
    if person.has_key("profile_jaccard_0_dot_35"):
        count6 = count6 + 1
    if person.has_key("profile_jaccard_0_dot_375"):
        count7 = count7 + 1
    if person.has_key("profile_jaccard_0_dot_4"):
        count8 = count8 + 1
    if person.has_key("profile_jaccard_0_dot_425"):
        count9 = count9 + 1
    if person.has_key("profile_jaccard_0_dot_45"):
        count10 = count10 + 1
    if person.has_key("profile_jaccard_0_dot_475"):
        count11 = count11 + 1
    if person.has_key("profile_jaccard_0_dot_5"):
        count12 = count12 + 1
    if person.has_key("profile_jaccard_0_dot_525"):
        count13 = count13 + 1
    # db_client.facebook_db.buet3.update(
    # {"_id": person["_id"]},
    # {
    #     "person": person["person"],
    #     "profiles": person["profiles"]
    # }
    # )

# print count
# print count1
# print count2
# print count3
# print count4
# print count5
# print count6
# print count7
# print count8
# print count9
# print count10
# print count11
# print count12
# print count13
# print zero