from aiogram import Router, types
from app.services.discounts import create_discount_code
from app.services.auth import is_admin

router = Router()

@router.message(lambda m: m.text.startswith("/adddiscount"))
async def add_discount(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("⛔️ فقط مدیر مجاز است.")
    
    parts = message.text.split()
    if len(parts) != 4:
        return await message.answer("فرمت: /adddiscount CODE PERCENT مدت(روز)")
    
    code = parts[1]
    percent = int(parts[2])
    days = int(parts[3])
    await create_discount_code(code, percent, days)
    await message.answer("✅ کد تخفیف ثبت شد.")
from aiogram import Router, types
from app.models.discount import DiscountCode
from app.services.db import async_session
from datetime import datetime, timedelta

router = Router()

@router.message(lambda m: m.text.startswith("➕ کد تخفیف"))
async def new_discount_code(message: types.Message):
    await message.answer("🔤 لطفاً کد تخفیف را وارد کنید (مثلاً: OFF30):")

@router.message(lambda m: len(m.text) < 12 and m.text.isalnum())
async def save_discount_code(message: types.Message):
    code = message.text.upper()
    async with async_session() as session:
        discount = DiscountCode(code=code, percent=30, expires_at=datetime.utcnow() + timedelta(days=7))
        session.add(discount)
        await session.commit()
        await message.answer(f"✅ کد تخفیف {code} با ۳۰٪ تخفیف برای ۷ روز فعال شد.")
