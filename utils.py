import os
from typing import Optional
from fastapi import HTTPException, UploadFile
from cloudinary.uploader import upload

def serialize_id(document: dict) -> dict:
    """Convert MongoDB ObjectId to string."""
    document["_id"] = str(document["_id"])
    return document

async def upload_image(file: UploadFile) -> Optional[str]:
    """Upload image to Cloudinary and return secure URL."""
    try:
        content = await file.read()
        result = upload(content, folder="products")
        return result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
