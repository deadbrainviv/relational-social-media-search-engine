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
# db_client.facebook_db.buet2.remove({"_id":ObjectId("5817c37d80d62e46dc8f8b59")});

print "Printing buet3 collection in facebook_db database:"
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    print person



















