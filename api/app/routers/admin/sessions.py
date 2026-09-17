import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.deps import require_admin
from app.redis_client import get_redis

router = APIRouter(prefix="/api/admin/sessions", tags=["admin-sessions"])


class SessionOut(BaseModel):
    session_id: str
    username: str
    nickname: str
    family_id: str | None = None
    admin_flag: bool = False


@router.get("", response_model=list[SessionOut])
async def list_sessions(current_user: dict[str, Any] = Depends(require_admin)):
    redis = get_redis()
    pattern = "reborn:session:*"
    keys = await redis.keys(pattern)
    sessions: list[SessionOut] = []
    for key in keys:
        sid = key.replace("reborn:session:", "")
        data = await redis.get(key)
        if data:
            payload = json.loads(data)
            sessions.append(
                SessionOut(
                    session_id=sid,
                    username=payload.get("username", ""),
                    nickname=payload.get("nickname", ""),
                    family_id=payload.get("familyId"),
                    admin_flag=payload.get("adminFlag", False),
                )
            )
    return sessions


@router.delete("/{session_id}")
async def kick_session(session_id: str, current_user: dict[str, Any] = Depends(require_admin)):
    redis = get_redis()
    key = f"reborn:session:{session_id}"
    deleted = await redis.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "已踢下线"}