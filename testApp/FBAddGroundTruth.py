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

fbexecute = FBExecute()
browser = fbexecute.login_into_facebook(creds_file="logins.txt")
name = "Gazi Salahuddin"
profile = "https://www.facebook.com/gsalahuddin"
visited_profile = fbexecute.visit_profile(browser, name, profile)
visited_profile["actual"] = "yes"
print visited_profile

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    if person["person"] == "Md. Salahuddin":
        print "For person", person["person"]
        person["profiles"].append(visited_profile)
        for profile in person["profiles"]:
            print profile["profile"]
        db_client.facebook_db.buet3.update(
            {"_id": person["_id"]},
            {
                "person": person["person"],
                "profiles": person["profiles"]
            }
        )


