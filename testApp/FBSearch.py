from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

# reading seeds directory
for file in os.listdir(os.getcwd() + "\\seeds\\"):
    filename = os.getcwd() + "\\seeds\\" + file
    print "#############################################################################################"
    data = open(filename, 'r').read()
    lines = data.split("\n")
    for line in lines:
        if line:
            name = line.split("  -  ")[0]
            link = line.split("  -  ")[1]
            print name, "==>", link.split("?")[0]

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

















