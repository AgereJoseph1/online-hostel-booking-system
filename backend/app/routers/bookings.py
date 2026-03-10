from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from .. import schemas
from ..auth import get_current_active_user
from ..database import get_db
from ..models import Booking, BookingStatus, Room

router = APIRouter(prefix="/bookings", tags=["bookings"])


async def is_room_available(db: AsyncSession, room_id: int, check_in: date, check_out: date) -> bool:
    if check_in >= check_out:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")

    overlap_condition = and_(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.CONFIRMED,
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    result = await db.execute(select(Booking).where(overlap_condition))
    existing = result.scalars().first()
    return existing is None


@router.post("/", response_model=schemas.BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: schemas.BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Room).where(Room.id == booking_in.room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    available = await is_room_available(db, booking_in.room_id, booking_in.check_in, booking_in.check_out)
    if not available:
        raise HTTPException(status_code=400, detail="Room is not available for the selected dates")

    booking = Booking(
        user_id=current_user.id,
        room_id=booking_in.room_id,
        check_in=booking_in.check_in,
        check_out=booking_in.check_out,
        status=BookingStatus.CONFIRMED,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


@router.get("/me", response_model=List[schemas.BookingOut])
async def list_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Booking).where(Booking.user_id == current_user.id))
    bookings = result.scalars().all()
    return bookings


@router.delete("/{booking_id}", response_model=schemas.BookingOut)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own bookings")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking already cancelled")

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking
