from typing import List, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: str = Field(..., alias="_id")
    type: str
    name: str
    unit: str
    reference: str
    price: float
    taxName: str
    taxRate: int
    total: float
    description: str
    image_url: Optional[str] = None
    active: bool
    class Config:
        populate_by_name = True


class ProductItem(BaseModel):
    row_id: str
    product: Product
    # productName: str
    reference: str
    price: float
    discount: float
    taxName: str
    taxRate: int
    quantity: int
    total: float

class Invoice(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    number: str = Field(..., unique=True)
    client_id: str
    client_name: str
    client_official_id: str
    client_phone: str
    operation_date: str
    type: str
    payment_method: str
    payment_period: str
    due_date: str
    products: List[ProductItem]
    subtotal: float
    discount: float
    taxable_base: float
    taxes: dict[str, float]
    total: float
    created_at: str
    status: str