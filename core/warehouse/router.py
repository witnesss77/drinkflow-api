from fastapi import APIRouter, status, HTTPException, Depends
from models.database import get_session
from sqlalchemy.exc import IntegrityError
from models.schemas import CreateWarehouse, UpdateWarehouse
from sqlalchemy import select
from models.models import Warehouse

router = APIRouter(prefix = "/warehouses")


@router.get("")
async def get_warehouses(db = Depends(get_session)):
    query = select(Warehouse)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_warehouse(request: CreateWarehouse, db = Depends(get_session)):
    warehouse = Warehouse(
        name = request.name,
        address = request.address
    )
    
    try:
        db.add(warehouse)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Warehouse already exists or unique constraint violated"
        )
    
    return {"status": status.HTTP_201_CREATED, "message": "Warehouse created successfully"}

@router.patch("/{warehouse_id:int}")
async def update_warehouse(warehouse_id, update: UpdateWarehouse, db = Depends(get_session)):
    query = select(Warehouse).where(Warehouse.id == warehouse_id)
    result = await db.execute(query)
    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(
            status_code=404,
            detail="Warehouse doesn't exist"
        )

    for k,v in update.model_dump(exclude_unset=True).items():
        if hasattr(warehouse, k):
            setattr(warehouse, k, v)
    try:
        await db.commit()
        await db.refresh(warehouse)
        return warehouse
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")

@router.delete("/{warehouse_id:int}")
async def delete_warehouse(warehouse_id, db = Depends(get_session)):
    query = select(Warehouse).where(Warehouse.id == warehouse_id)
    result = await db.execute(query)
    warehouse = result.scalar_one_or_none()

    if warehouse is None:
        raise HTTPException(
            status_code=404,
            detail="Warehouse doesnt exist"
        )
    
    await db.delete(warehouse)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Warehouse deleted successfully"}