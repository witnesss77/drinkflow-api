from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateStock, UpdateStock
from sqlalchemy import select
from core.models.models import Stock

router = APIRouter(prefix="/stocks")

@router.get("")
async def get_stocks(db = Depends(get_session)):
   query = select(Stock)
   result = await db.execute(query)
   return result.scalars().all()

@router.post("")
async def set_stocks(request: CreateStock, db = Depends(get_session)):
    if request.quantity < request.reserved_quantity:
        raise HTTPException(
            status_code=409,
            detail="Stock's reserved quantity cannot be more than existing quantity"
        )
    stock = Stock(
        drink_id = request.drink_id,
        warehouse_id = request.warehouse_id,
        quantity = request.quantity,
        reserved_quantity = request.reserved_quantity
    )
    try:
        db.add(stock)
        await db.commit()
        return stock
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Stock already exists or unique constraint violated"
        )


@router.patch("/{stock_id:int}")
async def update_stock(stock_id: int, request: UpdateStock, db = Depends(get_session)):
    query = select(Stock).where(Stock.id == stock_id)
    result = await db.execute(query)
    stock = result.scalar_one_or_none()

    if stock is None:
        raise HTTPException(status_code=404, detail="Stock doesn't exist")

    for k, v in request.model_dump(exclude_unset=True).items():
        setattr(stock, k, v)
    
    if stock.quantity < stock.reserved_quantity: 
        await db.rollback()
        raise HTTPException(status_code=409, detail="Stock's reserved quantity cannot be more than existing quantity")

    try:
        await db.commit()
        await db.refresh(stock)
        return stock
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
@router.delete("/{stock_id:int}")
async def delete_stock(stock_id: int, db = Depends(get_session)):
    query = select(Stock).where(Stock.id == stock_id)
    result = await db.execute(query)
    stock = result.scalar_one_or_none()

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Stock doesnt exist"
        )
    
    await db.delete(stock)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Stock deleted successfully"}