from typing import Any, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.redis_client import get_session


async def get_current_user(
    x_session_id: Optional[str] = Header(default=None),
) -> dict[str, Any]:
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少会话标识",
        )
    session = await get_session(x_session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期或账号已在其他设备登录",
        )
    if session.get("ban_flag"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被封禁",
        )
    return session


async def require_admin(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user_id = current_user.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效会话")
    result = await db.execute(select(User).where(User.id == user_id, User.deleted == False))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.admin_flag:
        raise HTTPException(status_code=403, detail="无权限访问后台管理")
    if user.ban_flag:
        raise HTTPException(status_code=403, detail="账号已被封禁")
    return current_user