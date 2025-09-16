from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os
app = FastAPI()

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class Product(BaseModel):
    id: str
    name: str
    price: float
    taxRate: int
    reference: str
    
# class Tax(BaseModel):
#     id: int
#     name: str
#     rate: int

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


INVOICES_FILE = "invoices.json"

def read_invoices() -> List[dict]:
    try:
        with open(INVOICES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_invoices(invoices: List[dict]):
    with open(INVOICES_FILE, "w") as f:
        json.dump(invoices, f, indent=2)

@app.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    return read_invoices()

@app.get("/invoices/count", response_model=int)
async def get_invoices_count():
    return len(read_invoices())

@app.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: Invoice):
    invoices = read_invoices()
    invoice_dict = invoice.dict()
    invoice_dict["number"] = str(len(invoices) + 1)  # Generate unique invoice number
    invoices.append(invoice_dict)
    write_invoices(invoices)
    return invoice_dict

@app.get("/products", response_model=List[Product])
async def get_products():
    products = [
        {"id": "1", "name": "Camisa Polo", "price": 20.99, "taxRate": 20, "reference": "S-001"},
        {"id": "2", "name": "Pantalón de mezclilla", "price": 45.5, "taxRate": 10, "reference": "P-001"},
    ]
    return products
    