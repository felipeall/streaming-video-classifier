import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

load_dotenv()


def connect_mongo_db():
    client = MongoClient("mongodb://localhost:27017")
    db = client[os.environ["TOPIC_NAME"]]

    return db


def create_collections_unique(db, videos_names):
    videos_map = {}
    for video in videos_names:
        video_collection = db[video]
        video_collection.create_index("frame", unique=True)
        videos_map.update({video: []})

    return videos_map


def insert_data_unique(db, videos_map):
    for video, docs in videos_map.items():
        video_collection = db[video]
        try:
            _result = video_collection.insert_many(docs)
            print("Bulk inserted documents:")
            for doc_id in _result.inserted_ids:
                print(doc_id)
            print()
        except BulkWriteError:
            print("Batch Contains Duplicate")
            for doc in docs:
                if video_collection.find_one({"frame": doc["frame"]}) is not None:
                    continue
                video_collection.insert_one(doc)
        except Exception as e:
            print(f"Error: {e}")
            pass
