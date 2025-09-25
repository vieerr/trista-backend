from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.analyticsService import (
    fetch_sales_over_time,
    fetch_top_products,
    fetch_top_customers
)

router = APIRouter()

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
        return await fetch_sales_over_time(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales data: {str(e)}")


@router.get("/top-products")
async def top_products(limit: int = 5):
    """
    Get top selling products by total value.
    """
    try:
        return await fetch_top_products(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top products: {str(e)}")


@router.get("/top-customers")
async def top_customers(limit: int = 5):
    """
    Get top customers by total spending.
    """
    try:
        return await fetch_top_customers(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top customers: {str(e)}")


@router.get("/dashboard-analytics")
async def dashboard_analytics():
    """
    Get dashboard analytics including sales over time, top products, and top customers.
    """
    try:
        sales_over_time = await fetch_sales_over_time()
        top_products = await fetch_top_products()
        top_customers = await fetch_top_customers()

        data = {
            "sales_over_time": sales_over_time,
            "top_products": top_products,
            "top_customers": top_customers
        }
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard analytics: {str(e)}")
