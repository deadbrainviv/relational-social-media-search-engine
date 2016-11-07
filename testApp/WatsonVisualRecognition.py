import json
from watson_developer_cloud import VisualRecognitionV3

api_key = "1ed546bbde9295c63c0b375bb566d164a0e0b646"
test_url = "https://www.ibm.com/ibm/ginni/images/ginni_bio_780x981_v4_03162016.jpg"
visual_recognition = VisualRecognitionV3("2016-05-20", api_key=api_key)

data = json.dumps(visual_recognition.detect_faces(images_url=test_url), indent=2)
data = json.loads(data)
for image in data["images"]:
    for face in image["faces"]:
        print face["age"]

