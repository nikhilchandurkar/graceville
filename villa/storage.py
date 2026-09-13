import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_mongo_client():
    """
    Returns a PyMongo MongoClient instance if MONGODB_URI is set.
    """
    mongo_uri = os.environ.get('MONGODB_URI')
    if not mongo_uri:
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB client: {e}")
        return None

def store_booking_in_mongo(inquiry_data):
    """
    Saves a booking inquiry document into MongoDB Atlas.
    """
    mongo_uri = os.environ.get('MONGODB_URI')
    if not mongo_uri:
        return False

    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        db_name = os.environ.get('MONGODB_DB_NAME', 'graceville_db')
        db = client[db_name]
        
        doc = dict(inquiry_data)
        doc['saved_at'] = datetime.utcnow()
        result = db.booking_inquiries.insert_one(doc)
        logger.info(f"Booking successfully stored in MongoDB Atlas with ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving booking to MongoDB Atlas: {e}")
        return False

def store_contact_in_mongo(contact_data):
    """
    Saves a contact message document into MongoDB Atlas.
    """
    mongo_uri = os.environ.get('MONGODB_URI')
    if not mongo_uri:
        return False

    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        db_name = os.environ.get('MONGODB_DB_NAME', 'graceville_db')
        db = client[db_name]
        
        doc = dict(contact_data)
        doc['saved_at'] = datetime.utcnow()
        result = db.contact_messages.insert_one(doc)
        logger.info(f"Contact message stored in MongoDB Atlas with ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving contact to MongoDB Atlas: {e}")
        return False

