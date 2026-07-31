from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateFactory, UpdateFactory
from sqlalchemy import select
from core.models.models import Factory

router = APIRouter(prefix = "/factories")


@router.get("")
async def get_factories(db = Depends(get_session)):
    query = select(Factory)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_factory(request: CreateFactory, db = Depends(get_session)):
    factory = Factory(
        name = request.name,
        location = request.location
    )

    try:
        db.add(factory)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Factory already exists or unique constraint violated"
        )
    
    return {"status": status.HTTP_201_CREATED, "message": "Factory created successfully"}

@router.patch("/{factory_id:int}")
async def update_factory(factory_id, update: UpdateFactory, db = Depends(get_session)):
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalar_one_or_none()

    if factory is None:
        raise HTTPException(
            status_code=404,
            detail="Factory doesn't exist"
        )

    for k,v in update.model_dump(exclude_unset=True).items():
        if hasattr(factory, k):
            setattr(factory, k, v)
    try:
        await db.commit()
        await db.refresh(factory)
        return factory
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error")

@router.delete("/{factory_id:int}")
async def delete_factory(factory_id, db = Depends(get_session)):
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalar_one_or_none()

    if factory is None:
        raise HTTPException(
            status_code=404,
            detail="Factory doesnt exist"
        )
    
    await db.delete(factory)
    await db.commit()
    return {"status": status.HTTP_200_OK, "message": "Factory deleted successfully"}