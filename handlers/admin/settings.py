from aiogram import Router, types
from app.services.auth import is_superadmin
from app.services.settings import update_setting

router = Router()

@router.message(lambda m: m.text.startswith("/set"))
async def update_setting_handler(message: types.Message):
    if not await is_superadmin(message.from_user.id):
        return await message.answer("⛔️ فقط سوپراَدمین دسترسی دارد.")

    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        return await message.answer("فرمت: /set کلید مقدار")
    
    key, value = parts[1], parts[2]
    await update_setting(key, value)
    await message.answer(f"✅ تنظیمات بروزرسانی شد: {key} = {value}")
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.services.settings import get_settings, update_setting
from app.utils.translation import t

router = Router()

class SettingsForm(StatesGroup):
    key = State()
    value = State()

@router.message(lambda msg: msg.text == t("admin_settings", "fa"))
async def show_settings(message: types.Message):
    settings = await get_settings()
    text = "⚙️ تنظیمات فعلی:\n"
    for k, v in settings.items():
        text += f"🔹 <b>{k}</b>: {v}\n"
    text += "\n🖋 برای تغییر یک مقدار، بنویس:\n/set_setting key value"
    await message.answer(text)

@router.message(F.text.startswith("/set_setting"))
async def set_setting(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            raise Exception("Invalid format")
        key, val = parts[1], parts[2]
        await update_setting(key, val)
        await message.answer(f"✅ مقدار جدید برای '{key}' ثبت شد.")
    except Exception as e:
        await message.answer("❌ فرمت صحیح: /set_setting key value")
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.services.settings import get_settings, update_setting
from app.utils.translation import t

router = Router()

class SettingsForm(StatesGroup):
    key = State()
    value = State()

@router.message(lambda msg: msg.text == t("admin_settings", "fa"))
async def show_settings(message: types.Message):
    settings = await get_settings()
    text = "⚙️ تنظیمات فعلی:\n"
    for k, v in settings.items():
        text += f"🔹 <b>{k}</b>: {v}\n"
    text += "\n🖋 برای تغییر یک مقدار، بنویس:\n/set_setting key value"
    await message.answer(text)

@router.message(F.text.startswith("/set_setting"))
async def set_setting(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            raise Exception("Invalid format")
        key, val = parts[1], parts[2]
        await update_setting(key, val)
        await message.answer(f"✅ مقدار جدید برای '{key}' ثبت شد.")
    except Exception as e:
        await message.answer("❌ فرمت صحیح: /set_setting key value")
