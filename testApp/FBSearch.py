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

fbexecute = FBExecute()
browser = fbexecute.login_into_facebook(creds_file="logins.txt")
print "Printing buet3 collection in facebook_db database:"
cursor = db_client.facebook_db.buet3.find()
flag = False
# for person in cursor:
#     for profile in person["profiles"]:
#         print profile["profile"], " ==> ", profile["friends"]
for person in cursor:
    for profile in person["profiles"]:
        if profile["profile"] == "https://www.facebook.com/Rafique.buet":
            flag = True
        if flag:
            print " --------------------------------------------------------------------------------------------------"
            print "Friends analyzed for:", person["person"], "and profile:", profile["profile"]
            time.sleep(3.0)
            response = browser.open(profile["profile"] + "/friends")
            html = response.read()
            lines = html.split("\n")
            profile["friends"] = []
            for line in lines:
                if "friends.search" in line:
                    line1 = line.split("https://www.facebook.com/")
                    friends = []
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
                    profile["friends"] = friends
                    print "Updating with new data:", profile["friends"]
                    break
    if flag:
        db_client.facebook_db.buet3.update(
        {"_id": person["_id"]},
        {
            "person": person["person"],
            "profiles": person["profiles"]
        }
        )
