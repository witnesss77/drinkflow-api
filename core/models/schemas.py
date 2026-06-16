from pydantic import BaseModel, Field, EmailStr
#дописать где необязательные поля после аннотации none = none




class CreateDrink(BaseModel):
    name: str
    desc: str
    alcoholic: bool
    price: int = Field(..., gt=0)
    factory_id: int = Field(...)


class UpdateDrink(BaseModel):
    name: str | None = Field(...)
    desc: str | None = None
    alcoholic: bool | None = Field()
    price: int = Field(..., gt=0)
    factory_id: int = Field(..., gt=0)


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
    reserved_quantity: int = Field(...)


class UpdateStock(BaseModel):
    drink_id: int | None = None
    warehouse_id: int | None = None
    quantity: int | None = None
    reserved_quantity: int | None = None


class CreateOrder(BaseModel):
    user_id: int = Field(...)
    warehouse_id: int = Field(...)
    status: str = Field(...)
    is_paid: bool = Field(...)


class UpdateOrder(BaseModel):
    user_id: int | None = None
    warehouse_id: int | None = None
    status: str | None = None 
    is_paid: bool | None = None


class CreateOrderItem(BaseModel):
    order_id: int = Field(...)
    user_id: int = Field(...)
    drink_id: int = Field(...)
    quantity: int = Field(..., gt=0)
    price_per_item: int = Field(..., gt=0)


class UpdateOrderItem(BaseModel):
    quantity: int | None = None
    price_per_item: int | None = None


class CreateUser(BaseModel):
    name: str = Field(...)
    email: str = EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(...)

class UpdateUser(BaseModel):
    name: str | None = None
    email: str = EmailStr()
    role: str 

class CreateWarehouse(BaseModel):
    name: str = Field(...)
    address: str = Field(...)

class UpdateWarehouse(BaseModel):
    name: str | None = None
    address: str | None = None