import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["trista"]
invoices_collection = db["invoices"]
products_collection = db["products"]

def get_db():
    """Returns the database instance."""
    return db

def get_invoices_collection():
    """Returns the invoices collection."""
    return invoices_collection

def get_products_collection():
    """Returns the products collection."""
    return products_collection
