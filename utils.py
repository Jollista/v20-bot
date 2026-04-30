import random
from discord import Color as color
import discord
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

"""
Connect to database, initialize prefix
"""

load_dotenv()
uri = os.getenv("MONGO")
print(uri)

# Create a new client and connect to the server
client:MongoClient = MongoClient(uri, server_api=ServerApi('1'))
db = client["v20"]
collection = db["guild prefixes"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)



"""
utility functions
"""

default_prefix = "$"

def query(id):
    try:
        return collection.find_one({"_id":id})
    except:
        return -1

def insert(post):
    collection.insert_one(post)

def update(id, up):
    collection.update_one({"_id":id}, {"$set":up})

def get_prefix(guild_id):
    result = query(guild_id)

    if result == None:
        insert({"_id":guild_id, "prefix":default_prefix})
        result = default_prefix
    else:
        result = result["prefix"]

    return result

def update_prefix(new_pre:str, guild_id):
    update(guild_id, {"prefix":new_pre})

def roll(number:int, size:int):
    results = []

    for i in range(number):
        results.append(random.randint(1, size))
    
    return results

def roll(size:int):
    return random.randint(1, size)

colors = [
        color.dark_blue(), color.dark_embed(), color.dark_gold(), color.dark_green(), color.dark_grey(), color.dark_magenta(),
        color.dark_orange(), color.dark_purple(), color.dark_red(), color.dark_teal(), color.dark_theme(), color.darker_grey()
    ]
def get_color():
    return colors[random.randint(0, len(colors)-1)]