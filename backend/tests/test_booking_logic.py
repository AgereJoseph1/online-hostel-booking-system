import asyncio
from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base
from app.models import Booking, BookingStatus, Room, Hostel, User, UserRole
from app.routers.bookings import is_room_available


@pytest.fixture(scope="module")
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_room_availability_no_overlap(test_db: AsyncSession):
    user = User(email="test@example.com", hashed_password="x", role=UserRole.GUEST)
    hostel = Hostel(name="Test Hostel", description=None, address="123 St", city="City", country="Country", owner=user)
    room = Room(name="Room 1", capacity=2, price_per_night=100, hostel=hostel)

    test_db.add_all([user, hostel, room])
    await test_db.commit()
    await test_db.refresh(room)

    today = date.today()
    check_in = today + timedelta(days=1)
    check_out = today + timedelta(days=3)

    available = await is_room_available(test_db, room.id, check_in, check_out)
    assert available is True


@pytest.mark.asyncio
async def test_room_availability_with_overlap(test_db: AsyncSession):
    result = await test_db.execute(select(Room))  # type: ignore
    room = result.scalars().first()

    today = date.today()
    existing_booking = Booking(
        user_id=1,
        room_id=room.id,
        check_in=today + timedelta(days=5),
        check_out=today + timedelta(days=10),
        status=BookingStatus.CONFIRMED,
    )
    test_db.add(existing_booking)
    await test_db.commit()

    available = await is_room_available(
        test_db,
        room.id,
        today + timedelta(days=7),
        today + timedelta(days=12),
    )
    assert available is False


@pytest.mark.asyncio
async def test_invalid_date_range_raises(test_db: AsyncSession):
    result = await test_db.execute(select(Room))  # type: ignore
    room = result.scalars().first()

    today = date.today()
    with pytest.raises(Exception):
        await is_room_available(test_db, room.id, today + timedelta(days=5), today + timedelta(days=4))
