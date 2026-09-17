from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.redis_client import create_session, delete_session, get_session
from app.schemas.auth_schemas import (
    LoginRequest, LoginResponse, LogoutResponse, ServerConfigResponse,
)
from app.schemas.user_schemas import UserOut
from app.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return ""


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username == payload.username, User.deleted == False)
    )
    user = result.scalar_one_or_none()

    password_ok = False
    if user and user.password:
        password_ok = verify_password(payload.password, user.password)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    if user.ban_flag:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账号已被封禁，解封时间：{user.ban_time or '永久'}，原因：{user.ban_reason or '未说明'}",
        )

    client_ip = _extract_client_ip(request)
    await db.execute(
        update(User).where(User.id == user.id).values(
            last_login_ip=client_ip,
            last_login_time=func.now(),
        )
    )
    await db.commit()
    await db.refresh(user)

    user_out = UserOut.model_validate(user)

    session_payload: dict[str, Any] = {
        "userId": str(user.id),
        "username": user.username,
        "nickname": user.nickname or user.username,
        "avatar": user.avatar or "",
        "familyId": str(user.family_id) if user.family_id else None,
        "adminFlag": user.admin_flag,
        "banFlag": user.ban_flag,
        "lastActiveTime": None,
    }
    session_id = await create_session(session_payload)

    return LoginResponse(
        message="登录成功",
        session_id=session_id,
        user=user_out,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict[str, Any] = Depends(get_current_user),
    x_session_id: str = Header(None),
):
    sid = x_session_id
    if not sid:
        raise HTTPException(status_code=400, detail="缺少会话标识")
    await delete_session(sid)
    return LogoutResponse()


@router.get("/me", response_model=UserOut)
async def me(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == current_user["userId"], User.deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserOut.model_validate(user)


@router.get("/session-info")
async def session_info(current_user: dict[str, Any] = Depends(get_current_user)):
    return current_user


@router.get("/server-config", response_model=ServerConfigResponse)
async def server_config():
    return ServerConfigResponse()