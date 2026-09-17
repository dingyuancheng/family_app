import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Family, Menu, User, UserMenu
from app.security import hash_password


async def create_default_admin():
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin = existing.scalar_one_or_none()

        if not admin:
            family = Family(name="默认家庭", description="系统初始化创建")
            session.add(family)
            await session.flush()

            admin = User(
                username="admin",
                nickname="超级管理员",
                password=hash_password("admin123"),
                admin_flag=True,
                family_id=family.id,
                status=1,
            )
            session.add(admin)
            family.member_count = 1
            await session.commit()
            print(f"[OK] 管理员已创建: admin / admin123")
        else:
            print(f"[SKIP] admin 用户已存在 (ID: {admin.id})")

        menus_result = await session.execute(
            select(Menu).where(Menu.deleted == False)
        )
        menus = list(menus_result.scalars().all())

        existing_perm_result = await session.execute(
            select(UserMenu.menu_id).where(UserMenu.user_id == admin.id)
        )
        existing_ids = {row[0] for row in existing_perm_result.all()}

        added = 0
        for menu in menus:
            if menu.id not in existing_ids:
                session.add(UserMenu(user_id=admin.id, menu_id=menu.id))
                added += 1

        if added:
            await session.commit()
            print(f"[OK] 已为 admin 分配 {added} 个菜单权限 (共 {len(menus)} 个)")
        else:
            print(f"[SKIP] admin 已有所有菜单权限")

        print(f"\n可使用以下账号登录:")
        print(f"  用户名: admin")
        print(f"  密码:   admin123")


if __name__ == "__main__":
    asyncio.run(create_default_admin())