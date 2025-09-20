from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from db import get_invoices_collection
from utils import serialize_id
from typing import Optional

router = APIRouter()
invoices_collection = get_invoices_collection()

@router.get("/sales-over-time")
async def sales_over_time(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get sales totals over time for charting.
    Dates must be in YYYY-MM-DD format.
    """
    try:
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {"$substr": ["$created_at", 0, 10]},  # group by date
                    "total": {"$sum": "$total"}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        result = list(invoices_collection.aggregate(pipeline))
        return [{"date": r["_id"], "value": r["total"]} for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales data: {str(e)}")


@router.get("/top-products")
async def top_products(limit: int = 5):
    """
    Get top selling products by total value.
    """
    try:
        pipeline = [
            {"$unwind": "$products"},
            {
                "$group": {
                    "_id": "$products.product.name",
                    "items": {"$sum": "$products.quantity"},
                    "total": {"$sum": "$products.total"}
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": limit}
        ]

        result = list(invoices_collection.aggregate(pipeline))
        return [
            {"concept": r["_id"], "items": r["items"], "total": r["total"]}
            for r in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top products: {str(e)}")


@router.get("/top-customers")
async def top_customers(limit: int = 5):
    """
    Get top customers by total spending.
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$client_name",
                    "documents": {"$sum": 1},
                    "total": {"$sum": "$total"}
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": limit}
        ]

        result = list(invoices_collection.aggregate(pipeline))
        return [
            {"concept": r["_id"], "documents": r["documents"], "total": r["total"]}
            for r in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top customers: {str(e)}")
