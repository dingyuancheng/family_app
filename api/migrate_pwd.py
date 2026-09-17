# migrate_pwd.py
import asyncio
from app.database import AsyncSessionLocal
from app.models import User
from app.security import pwd_context
from sqlalchemy import select


async def migrate_passwords():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        for user in users:
            # ⚠️重点！MD5哈希不能反向解密！你这里必须填写这个账号真实的明文密码！
            # 例如：user.username == "admin"，真实密码是 "123456"
            plain_password = "123456"
            user.password = pwd_context.hash(plain_password)
        await db.commit()

pty
if __name__ == "__main__":
    asyncio.run(migrate_passwords())
