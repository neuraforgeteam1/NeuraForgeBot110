from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import User, License
from database.queries import get_user_by_telegram_id, create_user, get_active_license
from services.license import generate_license_key, validate_license
from services.marketing import generate_referral_code, process_referral
from services.utils import get_user_language
from config import Config
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

config = Config()

class UserStates:
    SELECTING_PLAN = "user:selecting_plan"
    ENTERING_DEVICE_ID = "user:entering_device_id"

async def start(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    lang = message.from_user.language_code or 'en'
    
    if not user:
        user = await create_user(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
    
    # پردازش لینک دعوت
    if len(message.get_args()) > 0:
        if message.get_args().startswith('ref-'):
            referral_code = message.get_args()[4:]
            await process_referral(user, referral_code)
    
    text = get_user_language(lang).get('start', 'Welcome!')
    await message.answer(text)

async def buy_license(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    lang = user.language if user else 'en'
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    plans = ['1 ماهه', '3 ماهه', '6 ماهه', '1 ساله', '3 ساله', 'دائمی']
    keyboard.add(*plans)
    keyboard.add("❌ لغو")
    
    text = get_user_language(lang).get('select_plan', 'Please select a plan:')
    await message.answer(text, reply_markup=keyboard)
    await UserStates.SELECTING_PLAN.set()

async def process_plan_selection(message: types.Message, state: FSMContext):
    plan_map = {
        '1 ماهه': '1m',
        '3 ماهه': '3m',
        '6 ماهه': '6m',
        '1 ساله': '1y',
        '3 ساله': '3y',
        'دائمی': 'permanent'
    }
    
    selected_plan = plan_map.get(message.text)
    if not selected_plan:
        await message.answer("پلن انتخاب شده نامعتبر است.")
        return
    
    await state.update_data(selected_plan=selected_plan)
    
    text = "لطفاً شناسه دستگاه خود را وارد کنید:"
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await UserStates.ENTERING_DEVICE_ID.set()

async def process_device_id(message: types.Message, state: FSMContext):
    device_id = message.text.strip()
    if len(device_id) < 5:
        await message.answer("شناسه دستگاه باید حداقل ۵ کاراکتر باشد.")
        return
    
    user_data = await state.get_data()
    selected_plan = user_data['selected_plan']
    
    # ایجاد لایسنس
    user = await get_user_by_telegram_id(message.from_user.id)
    license_key = await generate_license_key(user.id, selected_plan)
    
    text = f"✅ لایسنس شما ایجاد شد!\n\n🔑 کلید: <code>{license_key}</code>\n\n📱 شناسه دستگاه: {device_id}"
    await message.answer(text, parse_mode="HTML")
    
    await state.finish()

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, Command("start"), state="*")
    dp.register_message_handler(buy_license, Command("buy"), state="*")
    dp.register_message_handler(buy_license, text="خرید لایسنس", state="*")
    
    dp.register_message_handler(
        process_plan_selection, 
        state=UserStates.SELECTING_PLAN
    )
    
    dp.register_message_handler(
        process_device_id, 
        state=UserStates.ENTERING_DEVICE_ID
    )# handlers/user.py

def register_user_handlers(dp: Dispatcher):
    # اینجا هندلرهای کاربران عادی را ثبت کنید
    from . import commands, messages, callbacks
    
    commands.register_commands(dp)
    messages.register_message_handlers(dp)
    callbacks.register_callback_handlers(dp)