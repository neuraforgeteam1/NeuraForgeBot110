from aiogram import Router, types
from app.services.license_manager import create_free_license
from app.services.auth import is_admin

router = Router()

@router.message(lambda m: m.text.startswith("/freelicense"))
async def grant_license(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("⛔️ فقط ادمین مجاز است.")
    
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("فرمت: /freelicense user_id duration(روز)")
    
    user_id = int(parts[1])
    duration = int(parts[2])
    result = await create_free_license(user_id=user_id, duration=duration)
    
    await message.answer("✅ لایسنس رایگان ساخته شد." if result else "❌ عملیات ناموفق.")
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.services.license_manager import create_free_license
from app.utils.translation import t

router = Router()

class FreeLicenseForm(StatesGroup):
    user_id = State()
    duration = State()
    note = State()

@router.message(lambda msg: msg.text == t("grant_free_license", "fa"))
async def ask_user_id(message: types.Message, state: FSMContext):
    await message.answer("🆔 لطفاً آی‌دی تلگرام کاربر را وارد کنید:")
    await state.set_state(FreeLicenseForm.user_id)

@router.message(FreeLicenseForm.user_id)
async def ask_duration(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("⏳ مدت زمان لایسنس را وارد کنید (روز - برای دائمی بنویس 0):")
    await state.set_state(FreeLicenseForm.duration)

@router.message(FreeLicenseForm.duration)
async def ask_note(message: types.Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await message.answer("📝 توضیح یا یادداشت برای این لایسنس:")
    await state.set_state(FreeLicenseForm.note)

@router.message(FreeLicenseForm.note)
async def confirm_license(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = int(data['user_id'])
    duration = int(data['duration'])
    note = message.text

    license_key = await create_free_license(user_id, duration, note)
    await state.clear()
    await message.answer(f"✅ لایسنس رایگان ساخته شد:\n🔐 <code>{license_key}</code>")
from aiogram import Router, types
from app.services.license_manager import create_license
from app.keyboards.inline import confirm_free_license
from app.models.user import get_user_by_username_or_id

router = Router()

@router.message(lambda msg: msg.text.startswith("🎁 لایسنس رایگان"))
async def handle_free_license(message: types.Message):
    await message.answer("لطفاً آی‌دی عددی یا @username کاربر را بفرستید:")

@router.message(lambda msg: msg.text.startswith("@") or msg.text.isdigit())
async def grant_free_license(message: types.Message):
    from_user = message.from_user
    user = await get_user_by_username_or_id(message.text.strip())
    if not user:
        await message.answer("❌ کاربر یافت نشد.")
        return

    # فرض: پلن تستی = 1، پروژه فعال = 1
    license = await create_license(user.id, plan_id=1, project_id=1, is_free=True)
    await message.answer(
        f"✅ لایسنس رایگان ساخته شد برای @{user.username or user.id}\n🔑 کد: {license.license_key}"
    )
