from testApp.FBExecute import *
from testApp.FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os
import operator

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect()

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    dict = {}
    profiles1 = []
    profiles = person["profiles"]
    for profile in profiles:
        dict[profile["profile"]] = profile
    for k, v in dict.iteritems():
        profiles1.append(v)
    person["profiles"] = profiles1
    # db_client.facebook_db.buet3.update(
    #     {"_id": person["_id"]},
    #     {
    #         "person": person["person"],
    #         "profiles": person["profiles"],
    #     }
    # )
































