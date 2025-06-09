from aiogram import Router, types
from app.utils.translation import t
from app.services.ai_helper import ask_gpt

router = Router()

@router.message(lambda msg: msg.text.startswith("/ask_ai"))
async def handle_ai_question(message: types.Message):
    question = message.text.replace("/ask_ai", "").strip()
    if not question:
        await message.answer("❓ لطفاً سوال خود را بعد از دستور بنویسید.")
        return

    await message.answer("🤖 در حال پردازش...")
    answer = await ask_gpt(question)
    await message.answer(answer)
