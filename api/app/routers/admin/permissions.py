import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_admin
from app.models import Menu, User, UserMenu
from app.schemas.menu_schemas import MenuSimpleOut

router = APIRouter(prefix="/api/admin/permissions", tags=["admin-permissions"])


class PermissionSetRequest(BaseModel):
    menu_ids: List[uuid.UUID]


@router.get("/{user_id}", response_model=list[MenuSimpleOut])
async def get_user_permissions(
    user_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id, User.deleted == False))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")

    menu_ids_stmt = select(UserMenu.menu_id).where(UserMenu.user_id == user_id)
    menu_ids_result = await db.execute(menu_ids_stmt)
    granted_ids = [row[0] for row in menu_ids_result.all()]

    if not granted_ids:
        return []

    menus_stmt = select(Menu).where(Menu.id.in_(granted_ids), Menu.deleted == False).order_by(Menu.sort.asc())
    menus_result = await db.execute(menus_stmt)
    menus = list(menus_result.scalars().all())
    return [MenuSimpleOut.model_validate(m) for m in menus]


@router.put("/{user_id}")
async def set_user_permissions(
    user_id: uuid.UUID,
    payload: PermissionSetRequest,
    current_user: dict[str, Any] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id, User.deleted == False))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")

    valid_menu_stmt = select(Menu.id).where(Menu.deleted == False)
    valid_menu_result = await db.execute(valid_menu_stmt)
    valid_menu_ids = {row[0] for row in valid_menu_result.all()}

    invalid_ids = [mid for mid in payload.menu_ids if mid not in valid_menu_ids]
    if invalid_ids:
        raise HTTPException(status_code=400, detail=f"存在无效菜单 ID: {len(invalid_ids)} 个")

    existing_stmt = select(UserMenu).where(UserMenu.user_id == user_id)
    existing_result = await db.execute(existing_stmt)
    existing_records = list(existing_result.scalars().all())

    existing_map = {r.menu_id: r for r in existing_records}
    new_ids = set(payload.menu_ids)
    existing_ids = set(existing_map.keys())

    for mid in existing_ids - new_ids:
        db.delete(existing_map[mid])

    for mid in new_ids - existing_ids:
        db.add(UserMenu(user_id=user_id, menu_id=mid))

    await db.commit()
    return {"message": "权限已更新", "granted_count": len(new_ids)}


@router.get("/all-menus/simple", response_model=list[MenuSimpleOut])
async def list_all_menus_simple(
    current_user: dict[str, Any] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Menu).where(Menu.deleted == False).order_by(Menu.sort.asc())
    )
    menus = list(result.scalars().all())
    return [MenuSimpleOut.model_validate(m) for m in menus]