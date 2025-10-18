import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env locally
load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "fastAPI_ToDo")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
