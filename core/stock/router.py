from fastapi import APIRouter, Depends
from core.models.schemas import CreateStock, UpdateStock
from core.dependencies import get_stocks_service


router = APIRouter(prefix="/stocks")

@router.get("")
async def get_stocks(service = Depends(get_stocks_service)):
    return await service.get_stocks()

@router.post("")
async def set_stocks(request: CreateStock, service = Depends(get_stocks_service)):
    return await service.set_stocks(request)

@router.patch("/{stock_id:int}")
async def update_stock(stock_id: int, request: UpdateStock, service = Depends(get_stocks_service)):
    return await service.update_stocks(request, stock_id)
    
@router.delete("/{stock_id:int}")
async def delete_stock(stock_id: int, service = Depends(get_stocks_service)):
    return await service.delete_stocks(stock_id)