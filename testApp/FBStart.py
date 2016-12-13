from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib
from operator import itemgetter
import os

db_host = "localhost"
db_port = 27017
db_client = FBDb.connect(db_host, db_port)

# colleges = []
# colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
# colleges.append("buet")

# fb = FBExecute()
# fb.get_info_about_people(input_file="input.txt", colleges=colleges, creds_file="logins.txt", db_host=db_host, db_port=db_port, replace=False)

# db_client.facebook_db.buet4.drop()
count = 0
profiles = []
cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        profiles.append(profile["profile"])
        count = count + 1
print len(profiles)
profiles = set(profiles)
print len(profiles)

    # db_client.facebook_db.buet3.update(
    #     {"_id": person["_id"]},
    #     {
    #         "person": person["person"],
    #         "profiles": person["profiles"]
    #     }
    # )
# dict = {}
# dict["score"] = 0
# dict["score1"] = 0
# dict["score2"] = 0
# dict["profile"] = "https://www.facebook.com/DrIftekharAnam/"
# dict["actual"] = "yes"
# dict["friends"] = []
# dict["name"] = "Dr. Iftekhar Anam"
# dict["pic"] = "https://scontent-dft4-2.xx.fbcdn.net/v/t1.0-9/12741859_829622840482257_6991609422952546545_n.jpg?oh=02cfd6f06369185ac4446b23595d6ed4&oe=58C7DAEB"
# dict["education"] = "Dr. Iftekhar Anam joined University of Asia Pacific (UAP) in 2000 with an excellent academic background, including honors like the Chancellors Awards for S.S.C. and H.S.C. results, University Gold Medal and Malik Akram Hossain (CE departmental) Gold medal at BUET and the highest distinctions in his post-graduate studies at University of Texas and Texas A&M University.Before joining UAP, he worked as a lecturer at BUET, Teaching and Research Assistant at The University Texas at Austin and Texas A&M University"
# dict["location"] = ""
# dict["work"] = "Porfessor, Dept. of Civil Engineering, University of Asia Pacific (This is a FAN PAGE, so dont get confused. This Page is run by his students.)"



