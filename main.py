import os
import cloudinary

from models import Invoice, Product
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.invoices import router as invoice_router
from routes.products import router as product_router

load_dotenv()

app = FastAPI(
    title="Trista Backend",
    description="Backend API for trista",
    version="1.0.0"
)

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

app.include_router(invoice_router, prefix="/invoices", tags=["Invoices"])
app.include_router(product_router, prefix="/products", tags=["Products"])

