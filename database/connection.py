import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class DatabaseConnection:
    """Class to connect to MongoDB database"""

    def __init__(self):
        load_dotenv()
        self.uri = f"mongodb+srv://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PWD")}@resumecluster.sczyi.mongodb.net/?retryWrites=true&w=majority&appName=ResumeCluster"
        self.client = None
        self.database = None
        self.collection = None


    def connect(self):
        # Create a new client and connect to the server
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged database deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
            self.client.close()

    def create_database(self, db_name:str):
        # Create a new database
        db = self.client[db_name]
        print(f"Database {db_name} created successfully!")
        self.database = db
    
    def create_collection(self, db, collection_name:str):
        #  Create a new collection
        collection = db[collection_name]
        print(f"Collection {collection_name} created successfully!")
        self.collection = collection

    def insert_document(self, document:dict):
        # Insert a new document
        res = self.collection.insert_one(document)
        print(res)
        print("Document inserted successfully!")


    def disconnect(self):
        self.client.close()
        print("Disconnected from MongoDB!")



if __name__ == "__main__":
    db = DatabaseConnection()
    db.connect()
    # db.disconnect()