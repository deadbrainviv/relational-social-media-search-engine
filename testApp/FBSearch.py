from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

target_profile = "https://www.facebook.com/gsalahuddin"
counter = 0
counter1 = 0

# cursor = db_client.facebook_db.buet3.find()
# for person in cursor:
#     for profile in person["profiles"]:
#         #print profile
#         for friend in profile["friends"]:
#             if friend == target_profile:
#                 counter = counter + 1
#             if friend == target_profile and profile["actual"] == "yes":
#                 counter1 = counter1 + 1
# counter2 = counter + counter1

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    person["profiles"] = sorted(person["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
    db_client.facebook_db.buet3.update(
    {"_id": person["_id"]},
    {
        "person": person["person"],
        "profiles": person["profiles"]
    }
    )

