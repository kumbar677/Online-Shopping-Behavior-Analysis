import os
import pandas as pd
from pymongo import MongoClient
from config import Config

_client = None

def get_db_connection():
    global _client
    if _client is None:
        try:
            # Initialize MongoDB Client
            mongo_uri = getattr(Config, 'MONGO_URI', 'mongodb://localhost:27017/')
            
            # Mask password for secure logging
            masked_uri = mongo_uri
            try:
                if '@' in mongo_uri and '://' in mongo_uri:
                    prefix, rest = mongo_uri.split('://', 1)
                    if '@' in rest:
                        user_pass, host = rest.rsplit('@', 1)
                        if ':' in user_pass:
                            user, _ = user_pass.split(':', 1)
                            masked_uri = f"{prefix}://{user}:***@{host}"
                        else:
                            masked_uri = f"{prefix}://***@{host}"
            except Exception:
                masked_uri = "invalid-uri-format"
                
            print(f"[DB CONNECT] Mongo URI: {masked_uri}")
            
            _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Force a connection test to make sure server is available
            _client.server_info()
            print("[DB CONNECT] Connected successfully to MongoDB!")
        except Exception as e:
            print(f"[DB CONNECT ERROR] Failed to connect to MongoDB: {e}")
            _client = None
            return None
            
    mongo_db_name = getattr(Config, 'MONGO_DB', 'shopping_analysis')
    return _client[mongo_db_name]

def fetch_data_as_dataframe(collection_name, query=None, projection=None, pipeline=None):
    db = get_db_connection()
    if db is None:
        return pd.DataFrame()
    try:
        collection = db[collection_name]
        if pipeline is not None:
            # Aggregation pipeline
            cursor = collection.aggregate(pipeline)
        else:
            # Standard query
            cursor = collection.find(query or {}, projection)
            
        data = list(cursor)
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        # Convert ObjectId to string for easy serializability
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)
        return df
    except Exception as e:
        print(f"Error fetching data from collection '{collection_name}': {e}")
        return pd.DataFrame()
