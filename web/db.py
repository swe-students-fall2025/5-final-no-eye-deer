# web/db.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/petdiary")

_client = MongoClient(MONGO_URI)
_db = _client["petdiary"]

def get_db():
    """Return the main database handle."""
    return _db
