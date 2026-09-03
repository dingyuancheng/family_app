from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse,responses={401: {"description": "用户名或密码错误"}})
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == payload.username)
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    password_ok = False
    if user and user.password:
        password_ok = verify_password(payload.password, user.password)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    return LoginResponse(message="登录成功", user=UserOut.model_validate(user))