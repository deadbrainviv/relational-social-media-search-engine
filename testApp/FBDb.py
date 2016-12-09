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

    # BUET 3

    @staticmethod
    def store_profile(db_client, dict):
        print "# Adding dict:", dict
        db_client.facebook_db.buet3.save(dict)

    @staticmethod
    def find_dict(db_client, person):
        entries = db_client.facebook_db.buet3.find({'person':{'$eq':person}})
        if entries.count() is 0:
            return None
        for entry in entries:
            return entry

    @staticmethod
    def remove_dict(db_client, person):
        db_client.facebook_db.buet3.remove({'person': {'$eq': person}})

    # BUET 4

    @staticmethod
    def store_profile1(db_client, dict):
        print "# Adding dict:", dict
        db_client.facebook_db.buet4.save(dict)

    @staticmethod
    def find_dict1(db_client, person):
        entries = db_client.facebook_db.buet4.find({'person': {'$eq': person}})
        if entries.count() is 0:
            return None
        for entry in entries:
            return entry

    @staticmethod
    def remove_dict1(db_client, person):
        db_client.facebook_db.buet4.remove({'person': {'$eq': person}})