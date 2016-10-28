from FBExecute import *
from FBDb import *

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)
db = db_client.facebook_db

colleges = []
colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
colleges.append("buet")

fbexecute = FBExecute()
fbexecute.get_info_about_people("input.txt", colleges, "logins.txt", db_host, db_port)
print "Printing BUET2:"
cursor = db.buet2.find()
for result in cursor:
    print result








