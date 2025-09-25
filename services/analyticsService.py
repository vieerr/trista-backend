from datetime import datetime
from typing import Optional
from db import get_invoices_collection

invoices_collection = get_invoices_collection()

async def fetch_sales_over_time(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Fetch sales totals over time for charting.
    Dates must be in YYYY-MM-DD format.
    """
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


async def fetch_top_products(limit: int = 5):
    """
    Fetch top selling products by total value.
    """
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


async def fetch_top_customers(limit: int = 5):
    """
    Fetch top customers by total spending.
    """
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
