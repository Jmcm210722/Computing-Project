"""MongoDB helper exposing a `db` object for raw PyMongo use.

This module centralizes connection configuration. It reads `MONGO_URI`
and `DB_NAME` from environment variables (defaults provided for local dev).
"""
import os
from pymongo import MongoClient

# Read configuration from environment with sensible defaults for development
MONGO_URI = (os.getenv("MONGO_URI") or "mongodb://localhost:27017").strip()
DB_NAME = (os.getenv("DB_NAME") or "bodybalance").strip()

_client = MongoClient(MONGO_URI)
db = _client[DB_NAME]

# Exporting `db` allows other modules to perform raw PyMongo operations,
# e.g. `db.workouts.find_one(...)`.
