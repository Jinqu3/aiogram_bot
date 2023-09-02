from aiogram import types,Bot,Dispatcher,executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import sqlite as sq
from config import TOKEN
import hashlib

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot,storage=storage)

class ProfileStatesGroup(StatesGroup):
    
    registration = State()
    login = State()
    photo = State()
    name = State()
    age = State()
    desc = State()
    
    login_change = State()

"""
Вспомогательные функции
"""
def create_keyboard()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/create"),KeyboardButton("/cancel"))
    return kb

def get_cancel()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/cancel"))
    return kb

def get_keyboard()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/registr"),KeyboardButton("/login")).add(KeyboardButton("/cancel"))
    return kb

def login_keyboard()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Забыл пароль"),KeyboardButton("/cancel"))
    return kb

def choice_menu()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Да"),KeyboardButton("Нет"))
    return kb

async def on_startup(_):
    await sq.db_start()
"""
Хендлеры запуска/вспомогательные
"""
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message)->None:
    start_text = "Добро пожаловать!\nДля начала нужно выполнить вход,для этого введите команду /registr или /login"
    await message.answer(text = start_text,
                        reply_markup=get_keyboard())
    await message.delete()

@dp.message_handler(commands=['create'])
async def create_profile(message:types.Message):   
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
    await message.answer("Ты точно хочешь это сделать?\nВ случае отмены процесс регистрации прервётся и данные не сохранятся",reply_markup=choice_menu())
   
@dp.message_handler(Text(equals=['Да','Нет']),state=[ProfileStatesGroup.photo,ProfileStatesGroup.name,ProfileStatesGroup.age,ProfileStatesGroup.desc])
async def cancel(message : types.Message,state :FSMContext):
    if message.text == 'Да':
        await message.answer("Отменил операцию",reply_markup=get_keyboard())
        await state.finish()
    else:
        await message.answer("Продолжим заполнение профиля",reply_markup=get_cancel())

@dp.message_handler(Text(equals=['Да','Нет']),state= [ProfileStatesGroup.login,ProfileStatesGroup.registration])
async def cancel(message : types.Message,state :FSMContext):
    await message.answer("Отменил операцию",reply_markup=get_keyboard())
    await state.finish()
"""
Хендлеры Регистрации
"""
@dp.message_handler(commands=['registr'],state=None)
async def registration(message:types.Message):
    if await sq.find_user(message.from_user.id):
        await message.reply("Ты уже зарегистрирован,для входа введи команду /login",reply_markup=get_keyboard())
    else:
        await message.reply("Придумай себе пароль",reply_markup=get_cancel())
        await ProfileStatesGroup.registration.set()

@dp.message_handler(state=ProfileStatesGroup.registration)
async def registration(message:types.Message,state : FSMContext):
    password = hashlib.md5(message.text.encode()).hexdigest()
    if await sq.find_user(message.from_user.id):
        await sq.set_password(message.from_user.id,password)
        await message.answer("Смена пароля произошла успешно!")
        await message.answer("Теперь ты можешь настроить свой профиль,для этого напиши команду /create",reply_markup=create_keyboard())
    else:
        await sq.create_profile_db(message.from_user.id,password)
        await message.answer("Регистрация прошла успешно,теперь ты можешь настроить свой профиль,для этого напиши команду /create",reply_markup=create_keyboard())
    await state.finish()
"""
Хендлеры логина
"""

@dp.message_handler(commands=['login'],state=None)
async def registration(message:types.Message):
    if await sq.find_user(message.from_user.id):
        await ProfileStatesGroup.login.set()
        await message.reply("Введи пароль",reply_markup=login_keyboard())
    else:
        await message.reply("Тебе нужно зарегистрироваться,для этого введи команду /registr",reply_markup=get_keyboard())
    
@dp.message_handler(Text(equals=('Забыл пароль')),state=ProfileStatesGroup.login)
async def forgot_password(message: types.Message):
    await message.answer("Хочешь поменять пароль?",reply_markup=choice_menu())
    await ProfileStatesGroup.login_change.set()

@dp.message_handler(Text(equals=['Да','Нет']),state=ProfileStatesGroup.login_change)
async def change_password(message: types.Message):
    if message.text == "Да":
        await message.answer("Введи новый пароль",reply_markup=get_cancel())
        await ProfileStatesGroup.registration.set()
    elif message.text == 'Нет':
        await message.reply("Введи пароль ещё раз",reply_markup=login_keyboard())
        await ProfileStatesGroup.login.set()
    else:
        await message.answer("Неверная команда",reply_markup=get_cancel())
        
@dp.message_handler(state=ProfileStatesGroup.login)
async def login(message:types.Message,state : FSMContext):
    password = hashlib.md5(message.text.encode()).hexdigest()
    if password != await sq.get_password(message.from_user.id):
        await message.answer("Неправильный пароль,попробуй ещё раз",reply_markup=login_keyboard())
    else:
        await message.answer("Вход прошёл успешно,теперь ты можешь настроить свой профиль,для этого напиши команду /create",reply_markup=create_keyboard())
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
        await sq.edit_profile_db(data,message.from_user.id)
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True,on_startup=on_startup)
