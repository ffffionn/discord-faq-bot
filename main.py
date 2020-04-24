import pymongo
import sys
from bot import Bot

if len(sys.argv) < 3:
    sys.exit("\t Usage:  main.py localhost:27017 <API_TOKEN>")

mongo = pymongo.MongoClient(sys.argv[1])
client = Bot(mongo)
client.run(sys.argv[2])
