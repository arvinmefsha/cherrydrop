from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
import asyncio

class Database:
    client: AsyncIOMotorClient = None
    database = None

database = Database()

async def get_database():
    return database.database

async def connect_to_mongo():
    """Create database connection"""
    MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
    database.client = AsyncIOMotorClient(MONGODB_URL)
    database.database = database.client.owlhacks_delivery
    
    # Test connection
    try:
        await database.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()