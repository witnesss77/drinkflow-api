from fastapi import APIRouter, status, HTTPException, Depends
from core.dependencies import get_factory_service
from core.models.schemas import CreateFactory, UpdateFactory
from core.auth.router import admin_check


router = APIRouter(prefix = "/factories")


@router.get("")
async def get_factories(service = Depends(get_factory_service)):
    return await service.get_factories()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_factory(request: CreateFactory, service = Depends(get_factory_service), user = Depends(admin_check)):
    if user is None:
        raise HTTPException(status_code=403, detail = "Unauthorized")
    return await service.set_factory(request)

@router.patch("/{factory_id:int}")
async def update_factory(factory_id, update: UpdateFactory, service = Depends(get_factory_service), user = Depends(admin_check)):
    if user is None:
        raise HTTPException(status_code=403, detail = "Unauthorized")
    return await service.update_factory(update, factory_id)

@router.delete("/{factory_id:int}")
async def delete_factory(factory_id, service = Depends(get_factory_service), user = Depends(admin_check)):
    if user is None:
        raise HTTPException(status_code=403, detail = "Unauthorized")
    return await service.delete_factory(factory_id)