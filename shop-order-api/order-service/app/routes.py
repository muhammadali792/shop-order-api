import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.redis_client import publish_order_event
from app.config import settings

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=schemas.OrderResponse, status_code=201)
async def create_order(
    payload:      schemas.OrderCreate,
    db:           Session = Depends(get_db),
    current_user: dict    = Depends(get_current_user)
):
    total      = 0.0
    order_items = []

    async with httpx.AsyncClient() as client:
        for item in payload.items:
            try:
                response = await client.get(
                    f"{settings.product_service_url}/products/{item.product_id}",
                    timeout=5.0
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found"
                    )
                product = response.json()
                if product["stock"] < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {item.product_id}"
                    )
                total += product["price"] * item.quantity
                order_items.append({
                    "product_id": item.product_id,
                    "quantity":   item.quantity,
                    "price":      product["price"]
                })
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Product service unavailable"
                )

    order = models.Order(user_id=current_user["id"], total=total)
    db.add(order)
    db.flush()

    for item_data in order_items:
        order_item = models.OrderItem(order_id=order.id, **item_data)
        db.add(order_item)

    db.commit()
    db.refresh(order)

    publish_order_event("order_created", {
        "order_id":   order.id,
        "user_id":    current_user["id"],
        "user_email": current_user["email"],
        "total":      total,
        "items":      order_items
    })

    return order

@router.get("/my", response_model=schemas.OrderListResponse)
def get_my_orders(
    current_user: dict    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user["id"]
    ).all()
    return {"total": len(orders), "orders": orders}

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id:     int,
    current_user: dict    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    order = db.query(models.Order).filter(
        models.Order.id      == order_id,
        models.Order.user_id == current_user["id"]
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{order_id}/cancel", response_model=schemas.OrderResponse)
def cancel_order(
    order_id:     int,
    current_user: dict    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    order = db.query(models.Order).filter(
        models.Order.id      == order_id,
        models.Order.user_id == current_user["id"]
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != models.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")

    order.status = models.OrderStatus.cancelled
    db.commit()
    db.refresh(order)

    publish_order_event("order_cancelled", {
        "order_id": order.id,
        "user_id":  current_user["id"]
    })

    return order
