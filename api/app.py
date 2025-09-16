from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import os
from bson import json_util
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["trista"]
invoices_collection = db["invoices"]

class Product(BaseModel):
    id: str
    name: str
    price: float
    taxRate: int
    reference: str

class ProductItem(BaseModel):
    id: str
    productId: str
    productName: str
    reference: str
    price: float
    discount: float
    taxName: str
    taxRate: int
    quantity: int
    total: float

class Invoice(BaseModel):
    number: str
    client: str
    type: str
    payment_method: str
    date: str
    due_date: str
    amount: float
    products: List[ProductItem]
    status: str

@app.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    invoices = list(invoices_collection.find())
    return json.loads(json_util.dumps(invoices))

@app.get("/invoices/count", response_model=int)
async def get_invoices_count():
    return invoices_collection.count_documents({})

@app.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: Invoice):
    invoice_count = invoices_collection.count_documents({})
    invoice_dict = invoice.dict()
    invoice_dict["number"] = str(invoice_count + 1)  # Generate unique invoice number
    invoices_collection.insert_one(invoice_dict)
    return invoice_dict

@app.get("/products", response_model=List[Product])
async def get_products():
    products = [
        {"id": "1", "name": "Camisa Polo", "price": 20.99, "taxRate": 20, "reference": "S-001"},
        {"id": "2", "name": "Pantalón de mezclilla", "price": 45.5, "taxRate": 10, "reference": "P-001"},
    ]
    return products

handler = Mangum(app)