from FBExecute import *
from FBDb import *

db_host = "localhost"
db_port = 27017

colleges = []
colleges.append("bangladesh university of engineering and technology")
colleges.append("buet")

fb_execute = FBExecute(db_host, db_port, colleges)

'''
token = fb_execute.get_facebook_token("C:\\Users\\IndervirSingh\\Documents\\GitHub\\fbsearch\\properties\\facebook_key")
people = fb_execute.get_input_people_list("C:\\Users\\IndervirSingh\\Documents\\GitHub\\fbsearch\\data\\forum_86_graduation.txt")
fb_execute.get_info_about_people(token, people)
'''

record = "{'past': [], 'home': [], 'studying': [], 'studied': ['at Bangladesh University of Engineering and Technology'], 'past_worked': [], 'current': ['Married to Shaila Rahman'], 'stays': ['Dhaka, Bangladesh'], 'went_to': ['St. Joseph&#039;s High School, Dhaka']}"
record = ast.literal_eval(record)
db_client = FBDb.connect_db(db_host, db_port)
FBDb.store_in_db(record, "Choudhary", db_client)
db = db_client.facebook_db
cursor = db.buet.find()
for result in cursor:
    print result






