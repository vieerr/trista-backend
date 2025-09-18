from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from models import Product
from utils import serialize_id, upload_image
from db import products_collection

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_products():
    """Retrieve all products from the database."""
    try:
        products = [serialize_id(product) for product in products_collection.find()]
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

@router.post("/", response_model=Product)
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
    """Create a new product with optional image upload."""
    try:
        product_dict = {
            "type": type,
            "name": name,
            "unit": unit,
            "reference": reference or "",
            "price": price,
            "taxName": taxName,
            "taxRate": taxRate,
            "total": total,
            "description": description or "",
            "image_url": await upload_image(image) if image else None,
        }

        inserted = products_collection.insert_one(product_dict)
        product_dict["_id"] = str(inserted.inserted_id)
        return Product(**product_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")