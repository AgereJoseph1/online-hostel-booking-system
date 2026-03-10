from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .. import schemas
from ..auth import get_current_owner
from ..database import get_db
from ..models import Hostel, Room

router = APIRouter(prefix="/hostels", tags=["hostels"])


@router.get("/", response_model=List[schemas.HostelOut])
async def list_hostels(
    db: AsyncSession = Depends(get_db),
    city: str | None = Query(default=None),
    country: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 50,
):
    query = select(Hostel).offset(skip).limit(limit)
    if city:
        query = query.where(Hostel.city.ilike(f"%{city}%"))
    if country:
        query = query.where(Hostel.country.ilike(f"%{country}%"))

    result = await db.execute(query)
    hostels = result.scalars().unique().all()
    return hostels


@router.get("/{hostel_id}", response_model=schemas.HostelOut)
async def get_hostel(hostel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hostel).where(Hostel.id == hostel_id))
    hostel = result.scalar_one_or_none()
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")
    return hostel


@router.post("/", response_model=schemas.HostelOut, status_code=status.HTTP_201_CREATED)
async def create_hostel(
    hostel_in: schemas.HostelCreate,
    db: AsyncSession = Depends(get_db),
    owner=Depends(get_current_owner),
):
    hostel = Hostel(**hostel_in.model_dump(), owner_id=owner.id)
    db.add(hostel)
    await db.commit()
    await db.refresh(hostel)
    return hostel


@router.put("/{hostel_id}", response_model=schemas.HostelOut)
async def update_hostel(
    hostel_id: int,
    hostel_in: schemas.HostelUpdate,
    db: AsyncSession = Depends(get_db),
    owner=Depends(get_current_owner),
):
    result = await db.execute(select(Hostel).where(Hostel.id == hostel_id))
    hostel = result.scalar_one_or_none()
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")
    if hostel.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="You can only update your own hostels")

    for field, value in hostel_in.model_dump(exclude_unset=True).items():
        setattr(hostel, field, value)

    await db.commit()
    await db.refresh(hostel)
    return hostel


@router.post("/{hostel_id}/rooms", response_model=schemas.RoomOut, status_code=status.HTTP_201_CREATED)
async def create_room(
    hostel_id: int,
    room_in: schemas.RoomCreate,
    db: AsyncSession = Depends(get_db),
    owner=Depends(get_current_owner),
):
    result = await db.execute(select(Hostel).where(Hostel.id == hostel_id))
    hostel = result.scalar_one_or_none()
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")
    if hostel.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="You can only add rooms to your own hostels")

    room = Room(**room_in.model_dump(), hostel_id=hostel_id)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.put("/{hostel_id}/rooms/{room_id}", response_model=schemas.RoomOut)
async def update_room(
    hostel_id: int,
    room_id: int,
    room_in: schemas.RoomUpdate,
    db: AsyncSession = Depends(get_db),
    owner=Depends(get_current_owner),
):
    result = await db.execute(select(Room).where(Room.id == room_id, Room.hostel_id == hostel_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.hostel.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="You can only update your own rooms")

    for field, value in room_in.model_dump(exclude_unset=True).items():
        setattr(room, field, value)

    await db.commit()
    await db.refresh(room)
    return room
