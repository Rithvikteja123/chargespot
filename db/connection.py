from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import MONGODB_URI, DATABASE_NAME

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]


def check_connection():
    """Return True when MongoDB responds; otherwise return False."""
    try:
        client.admin.command("ping")
        return True
    except PyMongoError as exc:
        print(f"MongoDB connection failed: {exc}")
        return False
