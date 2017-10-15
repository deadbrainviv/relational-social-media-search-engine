import pymongo


class FBDb:

    @staticmethod
    def connect(db_host, db_port):
        try:
            db_client = pymongo.MongoClient(db_host, db_port)
            return db_client
        except pymongo.errors.ServerSelectionTimeoutError as err:
            raise Exception("FBdb: Problem connecting to database!")
            return None

    @staticmethod
    def store_profile(db_client, collection, person):
        if collection == "buet3":
            db_client.facebook_db.buet3.save(person)

    @staticmethod
    def find_dict(db_client, collection, person):
        if collection == "buet3":
            entries = db_client.facebook_db.buet3.find({'person':{'$eq':person}})
            if entries.count() is 0:
                return None
            for entry in entries:
                return entry

    @staticmethod
    def remove_dict(db_client, collection, person):
        if collection == "buet3":
            db_client.facebook_db.buet3.remove({'person': {'$eq': person}})

    @staticmethod
    def get_cursor(db_client, collection):
        if collection == "buet3":
            return db_client.facebook_db.buet3.find()