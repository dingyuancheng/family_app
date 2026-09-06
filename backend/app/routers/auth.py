from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.schemas.user_schemas import UserOut
from app.security import verify_password
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"description": "用户名或密码错误"}},
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_by_username(db, payload.username)

    password_ok = False
    if user and user.password:
        password_ok = verify_password(payload.password, user.password)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    return LoginResponse(message="登录成功", user=UserOut.model_validate(user))