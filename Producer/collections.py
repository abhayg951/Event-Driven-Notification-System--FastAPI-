from .connection import get_db_connection

db = get_db_connection()


users_collection = db.get_collection("users")
notifications_collection = db.get_collection("notifications")
events_collection = db.get_collection("events")