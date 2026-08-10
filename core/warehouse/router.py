from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateWarehouse, UpdateWarehouse
from sqlalchemy import select
from core.models.models import Warehouse
from core.dependencies import get_warehouse_service

router = APIRouter(prefix = "/warehouses")


@router.get("")
async def get_warehouses(service = Depends(get_warehouse_service)):
    return await service.get_warehouses()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_warehouse(request: CreateWarehouse, service = Depends(get_warehouse_service)):
    return await service.set_warehouse(request)

@router.patch("/{warehouse_id:int}")
async def update_warehouse(warehouse_id, update: UpdateWarehouse, service = Depends(get_warehouse_service)):
    return await service.update_warehouse(update, warehouse_id)

@router.delete("/{warehouse_id:int}")
async def delete_warehouse(warehouse_id, service = Depends(get_warehouse_service)):
    return await service.delete_warehouse(warehouse_id)