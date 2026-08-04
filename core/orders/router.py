from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateOrder,CreateOrderItem, UpdateOrderItem, UpdateOrderStatus
from sqlalchemy import select
from core.models.models import Order, OrderItem, User, Stock
from core.service.order import OrderService
from core.auth.router import get_current_user

router = APIRouter(prefix = "/orders")

@router.get("")
async def get_orders(
    page: int | None = None,
    user_id: int | None = None,
    warehouse_id: int | None = None,
    status: str | None = None,
    is_paid: bool | None = None,
    db = Depends(get_session)):

    query = select(Order)

    if user_id:
        query = query.where(Order.user_id == user_id)
    if warehouse_id:
        query = query.where(Order.warehouse_id == warehouse_id)
    if status:
        query = query.where(Order.status == status)
    if is_paid is not None:
        query = query.where(Order.is_paid == is_paid)
        
    if page:
        items_offset = (page - 1) * 10
        query = query.offset(items_offset).limit(10)
        if query is None:
            query = select(Order).offset(items_offset).limit(10)
        result = await db.execute(query)
        return result.scalars().all()
    else:
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
    user_ = select(User).where(User.id == requested_user['id']).where(User.role == "manager" or User.role == "admin")
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
async def get_items(
    order_id: int | None = None,
    user_id: int | None = None,
    drink_id: int | None = None,
    quantity: int | None = None,
    pricier: int | None = None,
    db = Depends(get_session)):
    query = select(OrderItem)

    if order_id:
        query.where(OrderItem.order_id == order_id)
    if user_id:
        query.where(OrderItem.user_id == user_id)
    if drink_id:
        query.where(OrderItem.drink_id == drink_id)
    if quantity:
        query.where(OrderItem.quantity == quantity)
    if pricier:
        query.where(OrderItem.price_per_item < pricier)

    query = query.order_by(OrderItem.id)
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