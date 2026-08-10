from fastapi import APIRouter, status, HTTPException, Depends
from core.models.database import get_session
from core.dependencies import get_factory_service
from sqlalchemy.exc import IntegrityError
from core.models.schemas import CreateFactory, UpdateFactory
from sqlalchemy import select
from core.models.models import Factory

router = APIRouter(prefix = "/factories")


@router.get("")
async def get_factories(service = Depends(get_factory_service)):
    return await service.get_factories()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_factory(request: CreateFactory, service = Depends(get_factory_service)):
    return await service.set_factory(request)

@router.patch("/{factory_id:int}")
async def update_factory(factory_id, update: UpdateFactory, service = Depends(get_factory_service)):
    return await service.update_factory(update, factory_id)

@router.delete("/{factory_id:int}")
async def delete_factory(factory_id, service = Depends(get_factory_service)):
    return await service.delete_factory(factory_id)