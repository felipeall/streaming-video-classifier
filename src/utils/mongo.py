from pymongo import MongoClient


def connect_mongo_db():
    client = MongoClient("mongodb://localhost:27017")
    db = client["streaming-video-classifier"]

    return db
