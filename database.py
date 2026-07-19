from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = None
database = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = client.event_ticketing
    print("Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database():
    return database
