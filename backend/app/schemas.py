from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

from .models import UserRole, BookingStatus


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HostelBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    city: str
    country: str


class HostelCreate(HostelBase):
    pass


class HostelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class RoomBase(BaseModel):
    name: str
    capacity: int
    price_per_night: int


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[int] = None


class RoomOut(RoomBase):
    id: int

    class Config:
        from_attributes = True


class HostelOut(HostelBase):
    id: int
    owner_id: int
    rooms: List[RoomOut] = []

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    room_id: int
    check_in: date
    check_out: date


class BookingCreate(BookingBase):
    pass


class BookingOut(BookingBase):
    id: int
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True
