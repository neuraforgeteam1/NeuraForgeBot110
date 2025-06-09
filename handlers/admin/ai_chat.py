from aiogram import Router, types
from app.services.ai_helper import ask_gpt
from app.services.auth import is_user_active

router = Router()

@router.message(lambda m: m.text.startswith("/ask_ai"))
async def ai_handler(message: types.Message):
    if not await is_user_active(message.from_user.id):
        return await message.answer("⛔️ ابتدا لایسنس فعال تهیه کنید.")

    question = message.text.replace("/ask_ai", "").strip()
    if not question:
        return await message.answer("❓ سوال شما چیست؟")

    await message.answer("🤖 در حال بررسی...")
    response = await ask_gpt(question)
    await message.answer(response or "⛔️ خطا در دریافت پاسخ از هوش مصنوعی.")
