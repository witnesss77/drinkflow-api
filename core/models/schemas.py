from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class DrinkSchema(BaseModel):
    id: int
    name: str
    desc: str
    alcoholic: bool
    price: int 
    factory_id: int 

    class Config:
        from_attributes = True

class StockSchema(BaseModel):
    id: int
    drink_id: int
    warehouse_id: int 
    quantity: int
    reserved_quantity: int


    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id: int
    user_id: int 
    warehouse_id: int
    status:str
    is_paid: bool
    item_count: int
    total_price: int
    
    class Config:
        from_attributes = True

class CreateDrink(BaseModel):
    name: str
    desc: str
    alcoholic: bool
    price: int = Field(..., gt=0)
    factory_id: int = Field(...)


class UpdateDrink(BaseModel):
    name: str | None = None
    desc: str | None = None
    alcoholic: bool | None = None
    price: int | None = None
    factory_id: int | None = None


class CreateFactory(BaseModel):
    name: str = Field(...)
    location: str = Field(...)


class UpdateFactory(BaseModel):
    name: str | None = None
    location: str | None = None


class CreateStock(BaseModel):
    drink_id: int = Field(...)
    warehouse_id: int = Field(...)
    quantity: int = Field(..., gt=0)
    reserved_quantity: int = Field(..., ge=0)


class UpdateStock(BaseModel):
    quantity: int | None = Field(None, ge = 0)
    reserved_quantity: int | None = Field(None, ge = 0)


class CreateOrder(BaseModel):
    warehouse_id: int = Field(...)


class UpdateOrder(BaseModel):
    user_id: int | None = None
    warehouse_id: int | None = None
    status: str | None = None 
    is_paid: bool | None = None

class UpdateOrderStatus(BaseModel):
    status: str | None = None
    is_paid: bool | None = None


class CreateOrderItem(BaseModel):
    order_id: int = Field(...)
    drink_id: int = Field(...)
    quantity: int = Field(..., gt=0)



class UpdateOrderItem(BaseModel):
    quantity: int = Field(gt=0)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RoleEnum(str, Enum):
    admin = 'admin'
    user = 'user'
    manager = 'manager'


class CreateUser_admin(BaseModel):
    name: str = Field(...)
    email:  EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    role: RoleEnum


class CreateUser(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)



class UpdateUser(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: RoleEnum


class CreateWarehouse(BaseModel):
    name: str = Field(...)
    address: str = Field(...)


class UpdateWarehouse(BaseModel):
    name: str | None = None
    address: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str 