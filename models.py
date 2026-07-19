from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class SeatStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BOOKED = "booked"


class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class Seat(BaseModel):
    id: Optional[str] = None
    row: str
    number: int
    status: SeatStatus = SeatStatus.AVAILABLE
    price: float
    event_id: str
    reserved_by: Optional[str] = None
    reserved_at: Optional[datetime] = None


class Event(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    venue: str
    date: datetime
    total_seats: int
    rows: int
    seats_per_row: int
    base_price: float
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventCreate(BaseModel):
    title: str
    description: str
    venue: str
    date: datetime
    total_seats: int
    rows: int
    seats_per_row: int
    base_price: float


class Booking(BaseModel):
    id: Optional[str] = None
    user_id: str
    event_id: str
    seat_ids: List[str]
    total_amount: float
    payment_intent_id: Optional[str] = None
    payment_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookingCreate(BaseModel):
    event_id: str
    seat_ids: List[str]
