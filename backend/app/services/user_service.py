from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.create_date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()