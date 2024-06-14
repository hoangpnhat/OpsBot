from bson import ObjectId
import sys
import os
from typing import Dict

if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.database.mongodb import MongoDBConnection


class BaseCollection:
    def __init__(self, collection_name: str, db_connection: MongoDBConnection = MongoDBConnection()):
        self.collection_name = collection_name
        self.collection = db_connection.get_collection(collection_name)

    def insert_one(self, data: Dict) -> str:
        """Insert a new thread document into the collection."""
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def delete(self, id: str) -> bool:
        """Delete a thread document from the collection."""
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    def find_one(self, id: str) -> dict:
        """Find a single thread document by its ID."""
        result = self.collection.find_one({"_id": ObjectId(id)})
        if result:
            result["_id"] = str(result["_id"])
        return result

    def find_all(self) -> list:
        """Find all thread documents in the collection."""
        results = self.collection.find()
        return [{**row, "_id": str(row["_id"])} for row in results]
    