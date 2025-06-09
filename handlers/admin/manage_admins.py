from aiogram import Router, types
from app.services.auth import add_admin, remove_admin
from app.utils.translation import t

router = Router()

@router.message(lambda msg: msg.text == t("manage_admins", "fa"))
async def manage_admins_handler(message: types.Message):
    await message.answer("🛠 برای افزودن یا حذف ادمین، از دستور زیر استفاده کن:\n\n"
                         "/add_admin USER_ID\n/remove_admin USER_ID")

@router.message(lambda msg: msg.text.startswith("/add_admin"))
async def add_admin_cmd(message: types.Message):
    uid = int(message.text.split(" ")[1])
    await add_admin(uid)
    await message.answer("✅ ادمین اضافه شد")

@router.message(lambda msg: msg.text.startswith("/remove_admin"))
async def remove_admin_cmd(message: types.Message):
    uid = int(message.text.split(" ")[1])
    await remove_admin(uid)
    await message.answer("🗑 ادمین حذف شد")
from aiogram import Router, types
from app.models.user import User
from app.services.db import async_session
from sqlalchemy.future import select

router = Router()

@router.message(lambda m: m.text.startswith("➕ ادمین جدید"))
async def ask_admin_id(message: types.Message):
    await message.answer("👤 لطفاً آی‌دی عددی یا @username ادمین جدید را وارد کنید:")

@router.message(lambda m: m.text.lstrip("@").isalnum())
async def add_admin(message: types.Message):
    identifier = message.text.strip()
    async with async_session() as session:
        query = select(User).where((User.username == identifier.lstrip("@")) | (User.id == identifier))
        result = await session.execute(query)
        user = result.scalar()
        if not user:
            await message.answer("❌ کاربر یافت نشد.")
            return
        user.is_admin = True
        await session.commit()
        await message.answer(f"✅ کاربر {user.username or user.id} اکنون ادمین است.")

@router.message(lambda m: m.text.startswith("📋 لیست ادمین"))
async def list_admins(message: types.Message):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_admin == True))
        admins = result.scalars().all()
        text = "👮 لیست ادمین‌ها:\n\n"
        for a in admins:
            text += f"• {a.username or a.id} (زبان: {a.language or 'fa'})\n"
        await message.answer(text)
