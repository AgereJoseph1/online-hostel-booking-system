import asyncio

from . import Base, engine  # type: ignore


async def init_models():
    async with engine.begin() as conn:  # type: ignore
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
