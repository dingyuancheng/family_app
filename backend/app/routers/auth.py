import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.security import md5_hash

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    password_md5 = md5_hash(payload.password)
    stored_md5 = user.password if user is not None else ""
    password_ok = (
        bool(stored_md5)
        and len(stored_md5) == len(password_md5)
        and hmac.compare_digest(stored_md5, password_md5)
    )

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return LoginResponse(message="登录成功", user=UserOut.model_validate(user))
