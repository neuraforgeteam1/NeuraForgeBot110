from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from database.models import Transaction, License
from services.payment import create_payment, verify_payment
from services.license import activate_license
from services.utils import generate_invoice_pdf
from config import Config

config = Config()

class PaymentStates:
    SELECT_METHOD = "payment:select_method"
    PROCESS_BANK = "payment:process_bank"
    VERIFY_TRON = "payment:verify_tron"

async def start_payment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plan_type = user_data['selected_plan']
    device_id = user_data['device_id']
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💳 پرداخت با ترون (USDT)")
    keyboard.add("🏦 پرداخت کارت به کارت")
    keyboard.add("❌ لغو")
    
    await message.answer("روش پرداخت را انتخاب کنید:", reply_markup=keyboard)
    await PaymentStates.SELECT_METHOD.set()

async def select_payment_method(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plan_type = user_data['selected_plan']
    
    if message.text == "💳 پرداخت با ترون (USDT)":
        # ایجاد پرداخت ترون
        payment_info = await create_payment(
            user_id=message.from_user.id,
            plan_type=plan_type,
            method='tron'
        )
        
        await state.update_data(payment_info=payment_info)
        
        text = (
            f"💰 مبلغ قابل پرداخت: {payment_info['amount']} USDT\n\n"
            f"🔻 آدرس کیف پول:\n<code>{payment_info['address']}</code>\n\n"
            f"لطفاً مبلغ را به آدرس فوق ارسال کنید و سپس روی دکمه 'تایید پرداخت' کلیک کنید."
        )
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("✅ تایید پرداخت", "❌ لغو")
        
        await message.answer_photo(
            photo=payment_info['qr_code'],
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await PaymentStates.VERIFY_TRON.set()
    
    elif message.text == "🏦 پرداخت کارت به کارت":
        # ایجاد پرداخت بانکی
        payment_info = await create_payment(
            user_id=message.from_user.id,
            plan_type=plan_type,
            method='bank'
        )
        
        await state.update_data(payment_info=payment_info)
        
        text = (
            f"💰 مبلغ قابل پرداخت: {payment_info['amount']} تومان\n\n"
            f"💳 شماره کارت:\n<code>{payment_info['card_number']}</code>\n\n"
            f"پس از واریز، تصویر رسید را ارسال کنید."
        )
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("❌ لغو")
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await PaymentStates.PROCESS_BANK.set()

async def verify_tron_payment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    payment_info = user_data['payment_info']
    
    # تایید پرداخت
    verification = await verify_payment(
        user_id=message.from_user.id,
        trx_id="manual_verify",  # در حالت واقعی باید از کاربر دریافت شود
        amount=payment_info['amount'],
        plan_type=payment_info['plan_type']
    )
    
    if verification['success']:
        # فعال‌سازی لایسنس
        await activate_license(
            user_id=message.from_user.id,
            license_key=verification['license_key'],
            device_id=user_data['device_id']
        )
        
        # تولید فاکتور PDF
        invoice_path = await generate_invoice_pdf(verification['license_key'])
        
        text = (
            "✅ پرداخت شما با موفقیت تایید شد!\n\n"
            f"🔑 لایسنس شما: <code>{verification['license_key']}</code>\n\n"
            "فاکتور خرید در پیوست ارسال شد."
        )
        
        await message.answer(text, parse_mode="HTML")
        await message.answer_document(document=open(invoice_path, 'rb'))
    else:
        await message.answer("❌ پرداخت تایید نشد. لطفاً با پشتیبانی تماس بگیرید.")
    
    await state.finish()

async def process_bank_receipt(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("لطفاً تصویر رسید بانکی را ارسال کنید.")
        return
    
    # ذخیره تصویر رسید و انتظار برای تایید ادمین
    user_data = await state.get_data()
    payment_info = user_data['payment_info']
    
    # ایجاد تراکنش در حالت انتظار
    transaction = await Transaction.create(
        user_id=message.from_user.id,
        amount=payment_info['amount'],
        currency="IRR",
        description=f"خرید لایسنس {payment_info['plan_type']} (بانکی)",
        is_completed=False,
        admin_approved=False
    )
    
    text = (
        "📨 رسید بانکی شما دریافت شد و برای تایید به ادمین ارسال شد.\n\n"
        "پس از تایید، لایسنس برای شما فعال خواهد شد."
    )
    
    await message.answer(text)
    
    # ارسال به ادمین برای تایید
    admin_text = (
        "🔔 درخواست تایید پرداخت بانکی\n\n"
        f"👤 کاربر: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"💰 مبلغ: {payment_info['amount']} تومان\n"
        f"📝 توضیحات: {transaction.description}"
    )
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ تایید", callback_data=f"approve_bank_{transaction.id}"),
        types.InlineKeyboardButton("❌ رد", callback_data=f"reject_bank_{transaction.id}")
    )
    
    # ارسال به تمام ادمین‌ها
    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=message.photo[-1].file_id,
                caption=admin_text,
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error sending to admin {admin_id}: {e}")
    
    await state.finish()

def register_payment_handlers(dp: Dispatcher):
    dp.register_message_handler(start_payment, state=PaymentStates.SELECT_METHOD)
    dp.register_message_handler(select_payment_method, state=PaymentStates.SELECT_METHOD)
    dp.register_message_handler(verify_tron_payment, text="✅ تایید پرداخت", state=PaymentStates.VERIFY_TRON)
    dp.register_message_handler(process_bank_receipt, content_types=types.ContentType.PHOTO, state=PaymentStates.PROCESS_BANK)