from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.models import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity:   int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id:         int
    product_id: int
    quantity:   int
    price:      float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id:         int
    user_id:    int
    status:     OrderStatus
    total:      float
    items:      List[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    total:  int
    orders: List[OrderResponse]
