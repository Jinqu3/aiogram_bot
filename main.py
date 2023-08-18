from aiogram import types,Bot,Dispatcher,executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram.dispatcher import FSMContext

from sqlite import db_start,create_profile_db,edit_profile_db


TOKEN = "YOUR TOKEN"

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot,storage=storage)

class ProfileStatesGroup(StatesGroup):
    
    photo = State()
    name = State()
    age = State()
    desc = State()

"""
Вспомогательные функции
"""
def get_keyboard()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/create"))
    return kb

def get_cancel()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/cancel"))
    return kb

async def on_startup(_):
    await db_start()
"""
Хендлеры запуска/вспомогательные
"""
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message)->None:
    start_text = "Добро пожаловать!\nЧтобы создать профиль,введите команду /create"
    await message.answer(text = start_text,
                        reply_markup=get_keyboard())
    await message.delete()

@dp.message_handler(commands=['create'])
async def create_profile(message:types.Message):
    await create_profile_db(message.from_user.id)   
    await message.reply(text= "Давай создадим твой профиль.Для начала отправь своё фото",
                           reply_markup=get_cancel())
    await ProfileStatesGroup.photo.set()

"""
Хендлеры FSM
"""
@dp.message_handler(commands=['cancel'],state='*')
async def cancel(message : types.Message,state :FSMContext):
    if state is None:
        return
    await message.answer("Отменил регистрацию",reply_markup=get_keyboard())
    await state.finish()
"""
Хедлер ввода фото
"""
@dp.message_handler(lambda message: not message.photo ,state=ProfileStatesGroup.photo)
async def wrong_photo(message : types.Message):
    await message.reply("Это не фотография")

@dp.message_handler(content_types=['photo'],state=ProfileStatesGroup.photo)
async def load_photo(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['photo'] = message.photo[0].file_id #сохраняем идентификатор фото,который генерится API телеграма

        await message.reply('А теперь скажи своё имя')
        await ProfileStatesGroup.next()
"""
Хедлер ввода имени
"""
@dp.message_handler(lambda message: not message.text.isalpha() ,state=ProfileStatesGroup.name)
async def wrong_photo(message : types.Message):
    await message.reply("Неправильное имя")

@dp.message_handler(state=ProfileStatesGroup.name)
async def type_name(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['name'] = message.text #сохраням имя

        await message.reply('А теперь напиши свой возраст')
        await ProfileStatesGroup.next()
"""
Хедлер ввода возраста
"""
@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 120,state=ProfileStatesGroup.age)
async def wrong_photo(message : types.Message):
    await message.reply("Неправильный возраст")

@dp.message_handler(state=ProfileStatesGroup.age)
async def load_age(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['age'] = message.text #сохраням возраст

        await message.reply('А теперь расскажи немного о себе')
        await ProfileStatesGroup.next()
"""
Хедлер ввода описания
"""
@dp.message_handler(lambda message: len(message.text) > 255,state=ProfileStatesGroup.desc)
async def wrong_photo(message : types.Message):
    await message.reply("Хуя ты писатель,поменьше пжлста")

@dp.message_handler(state=ProfileStatesGroup.desc)
async def load_desc(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['desc'] = message.text #сохраням описание
        await message.reply(f'Хорошо,я тебя запомнил')
        await bot.send_photo(message.from_user.id,data['photo'],caption=f"Тебя зовут {data['name']},тебе {data['age']} лет\nВот немного информации  о тебе: {data['desc']}")
        await edit_profile_db(data,message.from_user.id)
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True,on_startup=on_startup)
