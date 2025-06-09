from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.translation import t
from app.services.db import async_session
from app.models.user import User

router = Router()

class BroadcastForm(StatesGroup):
    text = State()

@router.message(lambda msg: msg.text == t("broadcast", "fa"))
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer("📝 لطفاً پیام خود را وارد کنید:")
    await state.set_state(BroadcastForm.text)

@router.message(BroadcastForm.text)
async def confirm_broadcast(message: types.Message, state: FSMContext):
    text = message.text
    await state.clear()
    
    await message.answer("⏳ در حال ارسال پیام به کاربران...")

    success, fail = 0, 0
    async with async_session() as session:
        users = await session.execute(User.__table__.select())
        for u in users.fetchall():
            try:
                await message.bot.send_message(u.id, text)
                success += 1
            except:
                fail += 1

    await message.answer(f"📤 پیام به {success} نفر ارسال شد.\n❌ خطا در ارسال به {fail} نفر.")
