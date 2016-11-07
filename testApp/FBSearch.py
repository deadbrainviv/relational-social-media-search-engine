from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import json
from watson_developer_cloud import VisualRecognitionV3

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

counter = 0
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile.has_key("pic"):
            print "##############################################################################"
            counter = counter + 1
            print "Profile:",profile["pic"]
            api_key = "1ed546bbde9295c63c0b375bb566d164a0e0b646"
            visual_recognition = VisualRecognitionV3("2016-05-20", api_key=api_key)

            data = json.dumps(visual_recognition.detect_faces(images_url=profile["pic"]), indent=2)
            data = json.loads(data)
            for image in data["images"]:
                for face in image["faces"]:
                    print face["age"]
            if counter == 10:
                break




