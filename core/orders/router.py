from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
from models.schemas import CreateOrder, UpdateOrder, CreateOrderItem, UpdateOrderItem, UpdateOrderStatus
from sqlalchemy import select
from models.models import Order, OrderItem, User, Stock
from service.order import OrderService
from auth.router import get_current_user

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
        status = "created",
        is_paid = False
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

@router.patch("/{order_id:int}/payment")
async def update_order(order_id, db = Depends(get_session)):
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    query2 = select(OrderItem).where(OrderItem.order_id == order.id)
    result2 = await db.execute(query2)
    items = result2.scalars().all()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    if items is None:
        raise HTTPException(status_code=409, detail="order is empty")
    
    if order.is_paid == True or order.status == "paid":
        raise HTTPException(status_code=409, detail="order is already paid")
    
    order.is_paid = True
    order.status = "paid"

    await db.commit()
    await db.refresh(order)
    return order

@router.patch("/{order_id:int}/change_status")
async def update_order_status(request : UpdateOrderStatus, order_id, db = Depends(get_session), requested_user = Depends(get_current_user)):
    user_ = select(User).where(User.id == requested_user['id']).filter(User.role == "manager" or User.role == "admin")
    if user_ is None:
        return 'invalid user or role not allowed'
    
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    query2 = select(OrderItem).where(OrderItem.order_id == order.id)
    result2 = await db.execute(query2)
    items = result2.scalars().all()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    if items is None:
        raise HTTPException(status_code=409, detail="order is empty")
    
    order.status = request.status
    order.is_paid = request.is_paid

    await db.commit()
    await db.refresh(order)
    return order
    
@router.delete("/{order_id:int}")
async def delete_order(order_id, db = Depends(get_session)):
    return await OrderService.cancel_order(order_id, db)
    

@router.get("/order_items")
async def get_items(db = Depends(get_session)):
    query = select(OrderItem).order_by(OrderItem.id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/order_items")
async def set_items(warehouse_id: int, request: CreateOrderItem, db = Depends(get_session)):
    return await OrderService.add_order_item(request, warehouse_id, db)


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

    await OrderService.change_quantity(item_id, request, db)


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