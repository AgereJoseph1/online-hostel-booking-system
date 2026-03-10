import enum
from datetime import datetime, date

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class UserRole(str, enum.Enum):
    GUEST = "guest"
    OWNER = "owner"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    hostels: Mapped[list["Hostel"]] = relationship("Hostel", back_populates="owner")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


class Hostel(Base):
    __tablename__ = "hostels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="hostels")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="hostel", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_night: Mapped[int] = mapped_column(Integer, nullable=False)

    hostel: Mapped[Hostel] = relationship("Hostel", back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="room", cascade="all, delete-orphan")


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="bookings")
    room: Mapped[Room] = relationship("Room", back_populates="bookings")
