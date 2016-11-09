import json
from watson_developer_cloud import VisualRecognitionV3
from FBExecute import *
from FBDb import *

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

api_key = "7e56a3e69db4eb0b577b7004f130a13aea562009"
test_url = "https://scontent-dft4-2.xx.fbcdn.net/v/t1.0-1/c25.0.150.150/1016454_10203310158901805_2086236224_n.jpg?oh=8af2d85c2b0187e1fc1e4e3a82930950&oe=589DE90B"
visual_recognition = VisualRecognitionV3("2016-05-20", api_key=api_key)

counter0 = 0
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile.has_key("pic"):
            counter0 = counter0 + 1
            profile["age_watson"] = []
            profile["watson"] = []
    db_client.facebook_db.buet3.update(
        {"_id": person["_id"]},
        {
            "person": person["person"],
            "profiles": person["profiles"]
        }
    )
print "Total number of Facebook profiles cleared off:", counter0