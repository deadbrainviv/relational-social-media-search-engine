import json
from watson_developer_cloud import VisualRecognitionV3
from FBExecute import *
from FBDb import *

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

api_key = "0bdbbe5472be9743ab364cba068271573d170ab6"
test_url = "https://scontent-dft4-2.xx.fbcdn.net/v/t1.0-1/c25.0.150.150/1016454_10203310158901805_2086236224_n.jpg?oh=8af2d85c2b0187e1fc1e4e3a82930950&oe=589DE90B"
visual_recognition = VisualRecognitionV3("2016-05-20", api_key=api_key)

counter = 0
counter0 = 0
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile.has_key("pic") and not profile["watson"]:
            counter = counter + 1
        elif profile.has_key("pic") and profile["watson"]:
            counter0 = counter0 + 1
print "Total number of Facebook profiles to be update with age:", counter
print "Total number of Facebook profiles already updated with age:", counter0

counter1 = 0
counter2 = 0
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile.has_key("pic") and not profile["watson"]:
            print "-----------------------------------------------------------------------------------------------------"
            data = json.dumps(visual_recognition.detect_faces(images_url=profile["pic"]), indent=2)
            data = json.loads(data)
            # list = []
            # for image in data["images"]:
            #     for face in image["faces"]:
            #         list.append(face["age"])
            profile["watson"] = data
            print profile["pic"], profile["watson"]
            counter1 = counter1 + 1
            print "Total", counter1, "out of", counter, "have been done!"
        elif profile.has_key("pic") and profile["watson"]:
            counter2 = counter2 + 1
            print profile["watson"]
    # db_client.facebook_db.buet3.update(
    # {"_id": person["_id"]},
    # {
    #     "person": person["person"],
    #     "profiles": person["profiles"]
    # }
    # )

print "Total number of watson entries", counter2


