from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
from models.schemas import CreateOrder, UpdateOrder, CreateOrderItem, UpdateOrderItem
from sqlalchemy import select
from models.models import Order, OrderItem

router = APIRouter(prefix = "/orders")

@router.get("")
async def get_orders(db = Depends(get_session)):
    query = select(Order)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", status_code = status.HTTP_201_CREATED)
async def set_orders(request: CreateOrder, db = Depends(get_session)):
    order = Order(
        user_id = request.user_id,
        warehouse_id = request.warehouse_id,
        status = request.status,
        is_paid = request.is_paid
    )

    try:
        db.add(order)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Order already exists or unique constraint violated"
        )
    
    return {"status": status.HTTP_201_CREATED, "message": "Order created successfully"}

@router.patch("/{order_id:int}")
async def update_order(order_id, request: UpdateOrder, db = Depends(get_session)):
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    for k, v in request.model_dump(exclude_unset=True).items():
        setattr(order, k, v)

    try:
        await db.commit()
        await db.refresh(order)
        return order
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
@router.delete("/{order_id:int}")
async def delete_order(order_id, db = Depends(get_session)):
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order doesnt exist"
        )
    
    await db.delete(order)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Order deleted successfully"}

@router.get("/order_items")
async def get_items(db = Depends(get_session)):
    query = select(OrderItem).order_by(Order.id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/order_items", status_code = status.HTTP_201_CREATED)
async def set_items(request: CreateOrderItem, db = Depends(get_session)):
    item = OrderItem(
        order_id = request.order_id,
        user_id = request.user_id,
        drink_id = request.drink_id,
        quantity = request.quantity,
        price_per_item = request.price_per_item
    )

    try:
        db.add(item)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Order item already exists or unique constraint violated"
        )
    
    return {"status": status.HTTP_201_CREATED, "message": "Order item created successfully"}

@router.patch("/order_items/{item_id:int}")
async def update_items(item_id, request: UpdateOrderItem, db = Depends(get_session)):
    query = select(OrderItem).where(OrderItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    
    for k, v in request.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    try:
        await db.commit()
        await db.refresh(item)
        return item
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
@router.delete("/order_items/{item_id:int}")
async def delete_item(item_id, db = Depends(get_session)):
    query = select(OrderItem).where(OrderItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="OrderItem doesnt exist"
        )
    
    await db.delete(item)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Order item deleted successfully"}