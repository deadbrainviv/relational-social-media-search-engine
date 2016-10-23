import pymongo
from pymongo import MongoClient

class FBDb:

    @staticmethod
    def connect_db(dbHost, dbPort):
        try:
            client = pymongo.MongoClient(dbHost, dbPort)
            #print "Got the client:", client
            return client
        except pymongo.errors.ServerSelectionTimeoutError as err:
            raise Exception('Error: There is some problem connecting to Database, Please check connection and retry again, Note: data is not cached', 'Error')

    @staticmethod
    def store_in_db(record, db):
        FBDb.insert_record(record, db)

    @staticmethod
    def insert_record(record, db):
        db.buet1.save(record)

    @staticmethod
    def find_entry_in_db(db, id):
        entries = db.buet1.find({'id':{'$eq':id}})
        if entries.count() is 0:
            return None
        for entry in entries:
            return entry

    @staticmethod
    def form_db_record(self, recordJSON, email):
        try:
            record = recordJSON[recordKey]
            searchParams = record[gReqParamsKey]
            resultCount = record[resultCountKey]
            result = record[resultsKey]
            utcD = datetime.datetime.utcnow()
            utcDate = datetime.datetime.isoformat(utcD)
            dbRecord = {recordKey : {emailKey:email, searchParamsKey:searchParams, userUpdateKey:False, resultCountKey:resultCount, resultsKey:result, dateCreateKey:utcDate, dateUpdateKey:utcDate, createByKey:systemVal, updateByKey:systemVal, emailSentKey:False, emailSentCountKey:0}}
            return dbRecord
        except:
            raise Exception('Error : There is some problem with forming the record to store, might have happened because of change in LinkedIn JSOn Structure. Contact Administrator to verify formDBRecord definition', 'Error')
