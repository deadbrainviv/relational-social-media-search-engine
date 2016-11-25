from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

cursor = db_client.facebook_db.buet3.find()

list_images = []
for person in cursor:
    for profile in person["profiles"]:
        if profile.has_key("pic") and profile["actual"] == "yes":
            list_images.append(profile["pic"])

list_images = list(set(list_images))

count = 0
for image in list_images:
    image_name = "profile_" + str(count + 1) + ".jpg"
    urllib.urlretrieve(image, image_name)
    count = count + 1
    print count, "images done!"

print "Total profiles:", count
