from pymongo import MongoClient

#gets all collections in a database
def getCollections(database):
    client = MongoClient()
    names = client[database].collection_names()
    client.close()
    return names

#adds an entry to the specified database and collection
def addEntry(database,collection,entry):
    client = MongoClient()
    db = client[database]
    collection = db[collection]
    collection.insert_one(entry)
    client.close()

#lists all entries
def listEntry(database,collection):
    client = MongoClient()
    collection = client[database][collection]
    for entry in collection.find():
        print entry
    client.close()

#retrieves the specified entry
def getEntry(database,collection,query):
    client = MongoClient()
    collection = client[database][collection]
    entry = collection.find(query)
    client.close()
    return entry

#finds the entry in the specified database's collection
#matching the specifications in the query
#updates the fields from revisedEntry
def editEntry(database,collection,query,revisedEntry):
    client = MongoClient()
    collection = client[database][collection]
    entry = collection.find_one_and_update(query,{"$set":revisedEntry})
    client.close()

def deleteEntry(database,collection,query):
    client = MongoClient()
    collection = client[database][collection]
    print query
    entry = collection.delete_many(query)
    client.close()
