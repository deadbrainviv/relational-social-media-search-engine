import json
from watson_developer_cloud import VisualRecognitionV3
from FBExecute import *
from FBDb import *

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

api_key = "7e56a3e69db4eb0b577b7004f130a13aea562009"
test_url = "http://a5.files.biography.com/image/upload/c_fill,cs_srgb,dpr_1.0,g_face,h_300,q_80,w_300/MTE4MDAzNDEwNzg5ODI4MTEw.jpg"
visual_recognition = VisualRecognitionV3("2016-05-20", api_key=api_key)

data = json.dumps(visual_recognition.detect_faces(images_url=test_url), indent=2)
data = json.loads(data)
print data
for image in data["images"]:
    for face in image["faces"]:
        print face["age"]


