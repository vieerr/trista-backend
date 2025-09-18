import os

from fastapi import APIRouter
from typing import List
from datetime import datetime
from fastapi import HTTPException
from models import Invoice
from utils import serialize_id
from db import get_invoices_collection

router = APIRouter()
invoices_collection = get_invoices_collection()

# Invoice routes
@router.get("/", response_model=List[Invoice])
async def get_invoices():
    """Retrieve all invoices from the database."""
    try:
        invoices = [serialize_id(invoice) for invoice in invoices_collection.find()]
        return invoices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@router.get("/count", response_model=int)
async def get_invoices_count():
    """Get total count of invoices."""
    try:
        return invoices_collection.count_documents({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count invoices: {str(e)}")

@router.get("/{invoice_number}", response_model=Invoice)
async def get_invoice_by_id(invoice_number: str):
    """Retrieve a specific invoice by its number."""
    try:
        invoice = invoices_collection.find_one({"number": invoice_number})
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return serialize_id(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid invoice number: {str(e)}")

@router.post("/", response_model=Invoice)
async def create_invoice(invoice: Invoice):
    """Create a new invoice with an auto-incremented number."""
    try:
        invoice_count = invoices_collection.count_documents({})
        invoice_dict = invoice.model_dump()
        invoice_dict["number"] = str(invoice_count + 1)
        invoice_dict["created_at"] = datetime.utcnow().isoformat()

        result = invoices_collection.insert_one(invoice_dict)
        invoice_dict["_id"] = str(result.inserted_id)
        return invoice_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")
