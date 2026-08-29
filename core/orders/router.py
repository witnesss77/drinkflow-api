from fastapi import APIRouter, status, HTTPException, Depends, Request
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateOrder,CreateOrderItem, UpdateOrderItem, UpdateOrderStatus
from sqlalchemy import select
from core.dependencies import get_order_service
from core.models.models import Order, OrderItem, User
from core.orders.service import OrderLogicService
from core.auth.router import get_current_user

router = APIRouter(prefix = "/orders")

@router.get("")
async def get_orders(
    page: int | None = None,
    user_id: int | None = None,
    warehouse_id: int | None = None,
    status: str | None = None,
    is_paid: bool | None = None,
    service = Depends(get_order_service)):

    return await service.get_orders(page, user_id, warehouse_id, status, is_paid)
    

@router.post("", status_code = status.HTTP_201_CREATED)
async def set_orders(payload: CreateOrder, request: Request, service = Depends(get_order_service)):
    return await service.set_order(payload, request)

@router.patch("/{order_id:int}/payment")
async def update_order(order_id, service = Depends(get_order_service)):
    return await service.update_order_payment(order_id)

@router.patch("/{order_id:int}/change_status")
async def update_order_status(request: UpdateOrderStatus, order_id, requested_user = Depends(get_current_user), service = Depends(get_order_service)):
    return await service.update_order_status(request, order_id, requested_user)

@router.delete("/{order_id:int}")
async def delete_order(order_id, db = Depends(get_session)):
    return await OrderLogicService.cancel_order(order_id, db)
    

@router.get("/order_items")
async def get_items(
    order_id: int | None = None,
    user_id: int | None = None,
    drink_id: int | None = None,
    quantity: int | None = None,
    pricier: int | None = None,
    service = Depends(get_order_service)):

    return await service.get_items(order_id, user_id, drink_id, quantity, pricier)

@router.post("/order_items")
async def set_items(request: Request, warehouse_id: int, payload: CreateOrderItem, db = Depends(get_session)):
    return await OrderLogicService.add_order_item(request, payload, warehouse_id, db)


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

    return await OrderLogicService.change_quantity(item_id, request, db)


@router.delete("/order_items/{item_id:int}")
async def delete_item(item_id, service = Depends(get_order_service)):
    return await service.delete_item(item_id)