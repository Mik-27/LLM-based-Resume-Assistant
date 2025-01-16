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


    def connect(self):
        # Create a new client and connect to the server
        client = MongoClient(self.uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged database deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
            client.close()


    def disconnect(self):
        self.client.close()
        print("Disconnected from MongoDB!")