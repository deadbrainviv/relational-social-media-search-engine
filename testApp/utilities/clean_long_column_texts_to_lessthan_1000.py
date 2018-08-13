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
    profiles = person["profiles"]
    for profile in profiles:
        if profile.has_key("location"):
            if len(str(profile["location"].encode('utf-8'))) > 1000:
                profile["location"] = (str(profile["location"].encode('utf-8')))[:500]
                print profile["location"]
    # db_client.facebook_db.buet3.update(
    #     {"_id": person["_id"]},
    #     {
    #         "person": person["person"],
    #         "profiles": person["profiles"],
    #     }
    # )
































