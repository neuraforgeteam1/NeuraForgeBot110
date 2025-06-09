from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from database.models import User, License, AdminUser
from database.queries import get_user_by_telegram_id, create_user
from services.license import admin_generate_license
from services.utils import is_admin
from config import Config

config = Config()

class AdminStates:
    LOGIN = "admin:login"
    SELECT_ACTION = "admin:select_action"
    CREATE_LICENSE_SELECT_USER = "admin:create_license_select_user"
    CREATE_LICENSE_SELECT_PLAN = "admin:create_license_select_plan"
    SEND_NOTIFICATION = "admin:send_notification"

async def admin_login(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("دسترسی رد شد.")
    
    await AdminUser.filter(telegram_id=message.from_user.id).update(last_login=datetime.utcnow())
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("ایجاد لایسنس", "مدیریت کاربران")
    keyboard.add("ارسال اطلاعیه", "تنظیمات")
    keyboard.add("خروج از پنل")
    
    await message.answer("پنل مدیریت", reply_markup=keyboard)
    await AdminStates.SELECT_ACTION.set()

async def create_license_start(message: types.Message):
    await message.answer("شناسه کاربری را وارد کنید:")
    await AdminStates.CREATE_LICENSE_SELECT_USER.set()

async def process_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = await User.get_or_none(id=user_id)
        if not user:
            return await message.answer("کاربر یافت نشد.")
        
        await state.update_data(user_id=user_id)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for plan in ['1m', '3m', '6m', '1y', '3y', 'permanent']:
            keyboard.add(plan)
        keyboard.add("❌ لغو")
        
        await message.answer("پلن لایسنس را انتخاب کنید:", reply_markup=keyboard)
        await AdminStates.CREATE_LICENSE_SELECT_PLAN.set()
    except ValueError:
        await message.answer("شناسه کاربری معتبر نیست.")

async def process_license_plan(message: types.Message, state: FSMContext):
    plan = message.text
    if plan not in ['1m', '3m', '6m', '1y', '3y', 'permanent']:
        return await message.answer("پلن نامعتبر است.")
    
    data = await state.get_data()
    user_id = data['user_id']
    
    admin = await AdminUser.get(telegram_id=message.from_user.id)
    license = await admin_generate_license(
        user_id=user_id,
        plan_type=plan,
        admin_id=admin.id
    )
    
    await message.answer(f"✅ لایسنس ایجاد شد!\n\n🔑 کلید: <code>{license.license_key}</code>", parse_mode="HTML")
    await state.finish()
    await admin_login(message)

async def send_notification(message: types.Message):
    await message.answer("متن اطلاعیه را وارد کنید:")
    await AdminStates.SEND_NOTIFICATION.set()

async def process_notification_text(message: types.Message, state: FSMContext):
    # ارسال اطلاعیه به همه کاربران
    # کد ارسال به همه کاربران اینجا قرار می‌گیرد
    
    await message.answer("اطلاعیه با موفقیت ارسال شد.")
    await state.finish()
    await admin_login(message)

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_login, Command("admin"), state="*")
    dp.register_message_handler(create_license_start, text="ایجاد لایسنس", state=AdminStates.SELECT_ACTION)
    dp.register_message_handler(send_notification, text="ارسال اطلاعیه", state=AdminStates.SELECT_ACTION)
    
    dp.register_message_handler(
        process_user_id, 
        state=AdminStates.CREATE_LICENSE_SELECT_USER
    )
    
    dp.register_message_handler(
        process_license_plan, 
        state=AdminStates.CREATE_LICENSE_SELECT_PLAN
    )
    
    dp.register_message_handler(
        process_notification_text, 
        state=AdminStates.SEND_NOTIFICATION
    )