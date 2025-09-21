from bson import ObjectId
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
            "active": True
        }

        inserted = products_collection.insert_one(product_dict)
        product_dict["_id"] = str(inserted.inserted_id)
        return Product(**product_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Retrieve a single product by its ID."""
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_id(product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

@router.patch("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    type: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    unit: Optional[str] = Form(None),
    reference: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    taxName: Optional[str] = Form(None),
    taxRate: Optional[int] = Form(None),
    total: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    active: Optional[bool] = Form(None)
):
    """Update an existing product by its ID."""
    try:
        update_data = {k: v for k, v in {
            "type": type,
            "name": name,
            "unit": unit,
            "reference": reference,
            "price": price,
            "taxName": taxName,
            "taxRate": taxRate,
            "total": total,
            "description": description,
            "image_url": await upload_image(image) if image else None,
            "active": active
        }.items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        result = products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        updated_product = products_collection.find_one({"_id": ObjectId(product_id)})
        return serialize_id(updated_product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")
