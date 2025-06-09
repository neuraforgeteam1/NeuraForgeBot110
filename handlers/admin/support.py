from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.support import forward_to_admin

router = Router()

class SupportForm(StatesGroup):
    waiting_for_message = State()

@router.message(lambda m: m.text == "🛠 پشتیبانی")
async def support_start(message: types.Message, state: FSMContext):
    await message.answer("📩 پیام خود را بنویسید. مدیران بررسی می‌کنند.")
    await state.set_state(SupportForm.waiting_for_message)

@router.message(SupportForm.waiting_for_message)
async def support_submit(message: types.Message, state: FSMContext):
    await forward_to_admin(user_id=message.from_user.id, text=message.text)
    await message.answer("✅ پیام شما ارسال شد.")
    await state.clear()
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.translation import t

router = Router()

class SupportForm(StatesGroup):
    waiting_message = State()

@router.message(lambda msg: msg.text == t("support_btn", "fa"))
async def ask_support_message(message: types.Message, state: FSMContext):
    await message.answer(t("write_your_question", "fa"))
    await state.set_state(SupportForm.waiting_message)

@router.message(SupportForm.waiting_message)
async def receive_support_message(message: types.Message, state: FSMContext):
    await state.clear()

    support_text = f"""
📥 <b>پیام پشتیبانی جدید:</b>
👤 از طرف: @{message.from_user.username or '-'}
🆔 {message.from_user.id}
📩 متن: 
{message.text}

پاسخ دهید با:
/reply_to {message.from_user.id} پاسخ شما
"""
    await message.bot.send_message(chat_id="ADMIN_ID", text=support_text, parse_mode="HTML")
    await message.answer(t("support_received", "fa"))
@router.message(F.text.startswith("/reply_to"))
async def reply_to_user(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        user_id = int(parts[1])
        reply_text = parts[2]

        await message.bot.send_message(chat_id=user_id, text=f"📨 پاسخ پشتیبانی:\n\n{reply_text}")
        await message.answer("✅ پاسخ ارسال شد.")
    except:
        await message.answer("❌ فرمت دستور اشتباه است.")
