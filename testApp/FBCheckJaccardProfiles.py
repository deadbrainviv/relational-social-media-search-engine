from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

count = 0
cursor = db_client.facebook_db.buet3.find()
min = 1.0
max = 0.0
for person in cursor:
    flag = False
    for profile in person["profiles"]:
        if profile.has_key("score_jaccard_sim"):
            flag = True
    if flag:
        for profile in person["profiles"]:
            curr = profile["score_jaccard_sim"]
            if min > curr:
                min = curr
            if max < curr:
                max = curr
        count = count + 1
print count, min, max