from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
from bson import json_util
import json
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload 


load_dotenv()

app = FastAPI()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["trista"]
invoices_collection = db["invoices"]
products_collection = db["products"] 

class Product(BaseModel):
    type: str
    name: str
    unit: str
    reference: str
    price: float
    taxName: str
    taxRate: int
    total: float
    description: str
    image: Optional[UploadFile] = None

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
    invoice_dict["number"] = str(invoice_count + 1)  
    invoices_collection.insert_one(invoice_dict)
    return invoice_dict

@app.get("/products", response_model=List[Product])
async def get_products():
    products = list(products_collection.find())
    return json.loads(json_util.dumps(products))


@app.post("/products", response_model=Product)
async def create_product(
    type: str = Form(...),
    name: str = Form(...),
    unit: str = Form(...),
    reference: Optional[str] = Form(None),
    price: float = Form(...),
    taxName: str = Form(...),
    taxRate: int = Form(...),
    total: float = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    product_dict = {
        "type": type,
        "name": name,
        "unit": unit,
        "reference": reference,
        "price": price,
        "taxName": taxName,
        "taxRate": taxRate,
        "total": total,
        "description": description,
        "image_url": None,
    }

    if image:
        content = await image.read()
        result = upload(content, folder="products") 
        product_dict["image_url"] = result.get("secure_url")

    inserted = products_collection.insert_one(product_dict)
    product_dict["id"] = str(inserted.inserted_id)

    return Product(**product_dict)
