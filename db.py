# connection with MongoDb
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["app"]
users = db["users"]
questions = db["questions"]
results = db["results"]