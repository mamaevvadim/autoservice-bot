import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "7630062126:AAFTYJZ50fUHT7Qiq_X9vEFwgT2Uccrmyqw"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Booking(StatesGroup):
    service = State()
    car = State()
    time = State()
    name = State()
    phone = State()

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🧾 Оставить заявку", callback_data="book"),
        InlineKeyboardButton("🔧 Услуги", callback_data="services"),
        InlineKeyboardButton("❓ Вопросы", callback_data="faq"),
        InlineKeyboardButton("📍 Контакты", callback_data="contacts")
    )
    await message.answer_photo(photo="https://i.imgur.com/XNbdxxy.jpeg", caption=(
        "🚗 Добро пожаловать в автосервис DRIVE TECH!\n"
        "Я помогу вам оставить заявку, узнать цены или связаться с нами.\n\n"
        "Выберите действие ниже 👇"
    ), reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "book")
async def start_booking(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Диагностика", callback_data="service_Диагностика"),
        InlineKeyboardButton("🛢 Замена масла", callback_data="service_Замена масла"),
        InlineKeyboardButton("⚙ ТО", callback_data="service_ТО"),
        InlineKeyboardButton("🧰 Ремонт", callback_data="service_Ремонт")
    )
    await bot.send_message(callback_query.from_user.id, "Выберите услугу:", reply_markup=kb)
    await Booking.service.set()

@dp.callback_query_handler(lambda c: c.data.startswith("service_"), state=Booking.service)
async def ask_car(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.split("_")[1]
    await state.update_data(service=service)
    await bot.send_message(callback_query.from_user.id, "Введите марку и модель вашего авто:")
    await Booking.next()

@dp.message_handler(state=Booking.car)
async def choose_time(message: types.Message, state: FSMContext):
    await state.update_data(car=message.text)
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📆 Сегодня", callback_data="time_Сегодня"),
        InlineKeyboardButton("📆 Завтра", callback_data="time_Завтра"),
        InlineKeyboardButton("📝 Указать вручную", callback_data="time_Указать")
    )
    await message.answer("Когда вам удобно приехать?", reply_markup=kb)
    await Booking.next()

@dp.callback_query_handler(lambda c: c.data.startswith("time_"), state=Booking.time)
async def ask_name(callback_query: types.CallbackQuery, state: FSMContext):
    time = callback_query.data.split("_")[1]
    if time == "Указать":
        await bot.send_message(callback_query.from_user.id, "Напишите удобное время:")
    else:
        await state.update_data(time=time)
        await bot.send_message(callback_query.from_user.id, "Ваше имя?")
        await Booking.name.set()
        return
    await state.update_data(time="вручную")
    await Booking.time.set()

@dp.message_handler(state=Booking.time)
async def manual_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("Ваше имя?")
    await Booking.name.set()

@dp.message_handler(state=Booking.name)
async def ask_phone(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))
    await message.answer("Отправьте ваш номер телефона кнопкой ниже:", reply_markup=kb)
    await Booking.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Booking.phone)
async def confirm(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await message.answer(
        f"✅ Ваша заявка принята:\n"
        f"Услуга: {data['service']}\n"
        f"Авто: {data['car']}\n"
        f"Время: {data['time']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        "Мы свяжемся с вами в ближайшее время!", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "services")
async def show_services(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "🔍 Диагностика — от 1500 ₽\n"
        "🛢 Замена масла — от 1000 ₽\n"
        "⚙ ТО — от 2500 ₽\n"
        "🧰 Ремонт — по согласованию")

@dp.callback_query_handler(lambda c: c.data == "faq")
async def show_faq(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "🕒 Работаем с 9:00 до 20:00 ежедневно\n"
        "💳 Оплата наличными и картой\n"
        "🚘 Есть парковка\n"
        "🔄 Отмена заявки — за 2 часа")

@dp.callback_query_handler(lambda c: c.data == "contacts")
async def show_contacts(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "📍 Адрес: Москва, ул. Автомехаников, 10\n"
        "📞 Тел: +7 (900) 456-78-90\n"
        "📱 WhatsApp: @driveadmin")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
