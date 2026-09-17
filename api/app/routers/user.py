from typing import Any, List, Optional

import uuid
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Menu, MenuCategory, UserMenu, UserMenuClick
from app.schemas.menu_schemas import (
    MenuCategoryOut, MenuSimpleOut, MyMenusResponse,
)

router = APIRouter(prefix="/api/user", tags=["user"])


class MenuClickRequest(BaseModel):
    menu_id: uuid.UUID


@router.get("/my-menus", response_model=MyMenusResponse)
async def my_menus(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id_str = current_user["userId"]
    user_id = uuid.UUID(user_id_str)
    now = datetime.utcnow()

    menu_ids_stmt = select(UserMenu.menu_id).where(UserMenu.user_id == user_id)
    menu_ids_result = await db.execute(menu_ids_stmt)
    granted_menu_ids = [row[0] for row in menu_ids_result.all()]

    if not granted_menu_ids:
        return MyMenusResponse(categories=[], menus=[], frequent_menus=[])

    valid_menus_stmt = select(Menu).where(
        Menu.id.in_(granted_menu_ids),
        Menu.deleted == False,
        Menu.status == 1,
        Menu.visible == 1,
        or_(Menu.start_time == None, Menu.start_time <= now),
        or_(Menu.end_time == None, Menu.end_time >= now),
    ).order_by(Menu.sort.asc())
    valid_menus_result = await db.execute(valid_menus_stmt)
    valid_menus = list(valid_menus_result.scalars().all())

    if not valid_menus:
        return MyMenusResponse(categories=[], menus=[], frequent_menus=[])

    category_ids = list({m.category_id for m in valid_menus})
    categories_stmt = select(MenuCategory).where(
        MenuCategory.id.in_(category_ids),
        MenuCategory.deleted == False,
        MenuCategory.status == 1,
    ).order_by(MenuCategory.sort.asc())
    categories_result = await db.execute(categories_stmt)
    categories = list(categories_result.scalars().all())

    frequent_stmt = (
        select(UserMenuClick, Menu)
        .join(Menu, Menu.id == UserMenuClick.menu_id)
        .where(
            UserMenuClick.user_id == user_id,
            Menu.id.in_([m.id for m in valid_menus]),
            Menu.deleted == False,
        )
        .order_by(UserMenuClick.click_count.desc(), UserMenuClick.last_click.desc())
        .limit(6)
    )
    frequent_result = await db.execute(frequent_stmt)
    frequent_menus = [row[1] for row in frequent_result.all()]

    return MyMenusResponse(
        categories=[MenuCategoryOut.model_validate(c) for c in categories],
        menus=[MenuSimpleOut.model_validate(m) for m in valid_menus],
        frequent_menus=[MenuSimpleOut.model_validate(m) for m in frequent_menus],
    )


@router.post("/menu-click")
async def menu_click(
    payload: MenuClickRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = uuid.UUID(current_user["userId"])
    menu_id = payload.menu_id

    exists_stmt = select(UserMenuClick).where(
        UserMenuClick.user_id == user_id,
        UserMenuClick.menu_id == menu_id,
    )
    exists_result = await db.execute(exists_stmt)
    existing = exists_result.scalar_one_or_none()

    if existing:
        existing.click_count += 1
        existing.last_click = datetime.utcnow()
    else:
        new_record = UserMenuClick(
            user_id=user_id,
            menu_id=menu_id,
            click_count=1,
            last_click=datetime.utcnow(),
        )
        db.add(new_record)

    await db.commit()
    return {"message": "ok"}