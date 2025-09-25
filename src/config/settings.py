import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")


STATUS_COLUMN = os.getenv("STATUS_COLUMN", "insertion_status")
FIELDS_TO_EXTRACT = [
    "campaign_name", "where_do_you_located_in?", "full_name",
    "email", "phone_number", "zip_code", "state"
]

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS"))

CACHE_TTL= int(os.getenv("CACHE_TTL"))

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_CAMPAIGN_COLLECTION = os.getenv("MONGO_CAMPAIGN_COLLECTION")

LEAD_INSERTION_URL = os.getenv("LEAD_INSERTION_URL")
