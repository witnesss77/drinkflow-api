from fastapi import APIRouter, status, HTTPException, Depends, Request
from core.models.database import get_session
from core.auth.router import admin_check
from core.models.schemas import CreateOrder,CreateOrderItem, UpdateOrderItem, UpdateOrderStatus
from sqlalchemy import select
from core.dependencies import get_order_service
from core.models.models import OrderItem
from core.orders.service import OrderLogicService
from core.auth.router import get_current_user

router = APIRouter(prefix = "/orders")

@router.get("")
async def get_orders(
    page: int | None = None,
    warehouse_id: int | None = None,
    status: str | None = None,
    is_paid: bool | None = None,
    service = Depends(get_order_service), user = Depends(get_current_user)):

    return await service.get_orders(user, page, warehouse_id, status, is_paid)
    

@router.post("", status_code = status.HTTP_201_CREATED)
async def set_orders(payload: CreateOrder, request: Request, service = Depends(get_order_service), user = Depends(get_current_user)):
    return await service.set_order(payload, request, user_id = int(user['id']))

@router.patch("/{order_id:int}/payment")
async def update_order(order_id, service = Depends(get_order_service), user = Depends(get_current_user)):
    return await service.update_order_payment(order_id, user)

@router.patch("/{order_id:int}/change_status")
async def update_order_status(request: UpdateOrderStatus, order_id,service = Depends(get_order_service), user = Depends(admin_check)):
    return await service.update_order_status(request, order_id, user)

@router.delete("/{order_id:int}")
async def delete_order(order_id, db = Depends(get_session), user = Depends(admin_check)):
    return await OrderLogicService.cancel_order(order_id, db)
    

@router.get("/order_items")
async def get_items(
    order_id: int | None = None,
    drink_id: int | None = None,
    quantity: int | None = None,
    pricier: int | None = None,
    service = Depends(get_order_service), 
    user = Depends(get_current_user)):

    return await service.get_items(order_id, drink_id, quantity, pricier, user)

@router.post("/order_items")
async def set_items(request: Request, payload: CreateOrderItem, db = Depends(get_session), id_ = Depends(get_current_user)):
    return await OrderLogicService.add_order_item(request, payload, db, id_)


@router.patch("/order_items/{item_id:int}")
async def update_items(item_id, payload: UpdateOrderItem, request: Request, db = Depends(get_session), user = Depends(get_current_user)):
    query = select(OrderItem).where(OrderItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

    return await OrderLogicService.change_quantity(item_id, payload, request, db, user)


@router.delete("/order_items/{item_id:int}")
async def delete_item(item_id, request: Request, user = Depends(admin_check), db = Depends(get_session)):
    return await OrderLogicService.remove_item(item_id, request, db)