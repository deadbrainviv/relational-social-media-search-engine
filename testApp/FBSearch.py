from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

# fbexecute = FBExecute()
# fbexecute.get_info_about_people("input.txt", colleges, "logins.txt", db_host, db_port, True)

print "Printing buet2 collection in facebook_db database:"
cursor = db_client.facebook_db.buet2.find()
for person in cursor:
    print person
    # for profile in person["profiles"]:
    #     profile["actual"] = "no"
    # db_client.facebook_db.buet2.update(
    #     {"_id": person["_id"]},
    #     {
    #         "person": person["person"],
    #         "profiles": person["profiles"]
    #     }
    # )















