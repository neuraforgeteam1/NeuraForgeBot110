from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise
from config import Config
from .models import User, License, Referral, Transaction, Reward, AdminUser

config = Config()

TORTOISE_ORM = {
    "connections": {"default": config.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(
        config=TORTOISE_ORM
    )
    await Tortoise.generate_schemas(safe=True)
    
    # ایجاد ادمین پیش‌فرض
    for admin_id in config.ADMIN_IDS:
        if not await AdminUser.filter(telegram_id=admin_id).exists():
            await AdminUser.create(
                telegram_id=admin_id,
                username=f"admin_{admin_id}",
                role="superadmin",
                is_active=True
            )

async def close_db():
    await Tortoise.close_connections()