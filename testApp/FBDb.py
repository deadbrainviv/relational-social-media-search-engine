import pymongo
from pymongo import MongoClient

class FBDb:

    @staticmethod
    def connect(db_host, db_port):
        try:
            client = pymongo.MongoClient(db_host, db_port)
            #print "Got the client:", client
            return client
        except pymongo.errors.ServerSelectionTimeoutError as err:
            raise Exception('Error: There is some problem connecting to Database, Please check connection and retry again, Note: data is not cached', 'Error')

    @staticmethod
    def store_profile(db_client, dict):
        #print "# Adding dict:", dict
        db_client.facebook_db.buet2test.save(dict)

    @staticmethod
    def find_dict(db_client, person):
        entries = db_client.facebook_db.buet2test.find({'person':{'$eq':person}})
        if entries.count() is 0:
            return None
        for entry in entries:
            return entry

    @staticmethod
    def remove_dict(db_client, person):
        db_client.facebook_db.buet2test.remove({'person': {'$eq': person}})