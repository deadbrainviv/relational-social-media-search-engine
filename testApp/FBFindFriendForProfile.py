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

target_profile = "https://www.facebook.com/gsalahuddin"

print "Friends analyzed for:", target_profile
response = browser.open("https://www.facebook.com/gsalahuddin/friends")
html = response.read()
lines = html.split("\n")
friends = []
for line in lines:
    if "friends.search" in line:
        line1 = line.split("https://www.facebook.com/")
        for itr in line1:
            if not itr.startswith("<div class="):
                itr = itr.split("\"")[0]
                if "&amp;" in itr:
                    itr = itr.split("&amp;")[0]
                if "?fref=pb" in itr:
                    itr = itr.split("?fref=pb")[0]
                if "?ref=br" in itr:
                    itr = itr.split("?ref=br")[0]
                if itr.endswith("/"):
                    itr = itr[:-1]
                itr = "https://www.facebook.com/" + itr.strip()
                itr = itr.lower()
                if not itr.startswith("https://www.facebook.com/pages") and not "university" in itr and not "-" in itr:
                    friends.append(itr)
        friends = list(set(friends))
        print "Updating with new data:", friends

cursor = db_client.facebook_db.buet3.find()
for person in cursor:
    for profile in person["profiles"]:
        if profile["profile"] == target_profile:
            profile["friends"] = friends
            print profile
    # db_client.facebook_db.buet3.update(
    # {"_id": person["_id"]},
    # {
    #     "person": person["person"],
    #     "profiles": person["profiles"]
    # }
    # )

