
from aiogram.dispatcher import FSMContext
from aiogram import types,Dispatcher
from keyboards import *
from create_bot import bot,ProfileStatesGroup
import sqlite as sq

"""
Хендер создания профиля
"""
async def create_profile(message:types.Message):   
    await message.reply(text= "Давай создадим твой профиль.Для начала отправь своё фото",
                           reply_markup=get_cancel())
    await ProfileStatesGroup.photo.set()
"""
Хедлер ввода фото
"""
async def wrong_photo(message : types.Message):
    await message.reply("Это не фотография")

async def load_photo(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['photo'] = message.photo[0].file_id #сохраняем идентификатор фото,который генерится API телеграма

        await message.reply('А теперь скажи своё имя')
        await ProfileStatesGroup.next()

"""
Хедлер ввода имени
"""
async def wrong_name(message : types.Message):
    await message.reply("Неправильное имя")

async def load_name(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['name'] = message.text #сохраням имя

        await message.reply('А теперь напиши свой возраст')
        await ProfileStatesGroup.next()
"""
Хедлер ввода возраста
"""
async def wrong_age(message : types.Message):
    await message.reply("Неправильный возраст")

async def load_age(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['age'] = message.text #сохраням возраст

        await message.reply('А теперь расскажи немного о себе')
        await ProfileStatesGroup.next()
"""
Хедлер ввода описания
"""
async def wrong_desc(message : types.Message):
    await message.reply("Поменьше текста пжлста")

async def load_desc(message:types.Message,state:FSMContext):
    async with state.proxy() as data: #открываем локальное хранилище,Для хранения инфы(словарь)
        data['desc'] = message.text #сохраням описание
        await message.reply(f'Хорошо,я тебя запомнил')
        await bot.send_photo(message.from_user.id,data['photo'],
                             caption=f"Тебя зовут {data['name']},тебе {data['age']} лет\nВот немного информации  о тебе: {data['desc']}")
        await sq.edit_profile_db(data,message.from_user.id)
    await state.finish()


def register_handlers_profile(dp: Dispatcher):
    dp.register_message_handler(create_profile,commands=['create'])
    dp.register_message_handler(wrong_photo,lambda message: not message.photo ,state=ProfileStatesGroup.photo)
    dp.register_message_handler(load_photo,content_types=['photo'],state=ProfileStatesGroup.photo)
    dp.register_message_handler(wrong_name,lambda message: not message.text.isalpha() ,state=ProfileStatesGroup.name)
    dp.register_message_handler(load_name,state=ProfileStatesGroup.name)
    dp.register_message_handler(wrong_age,lambda message: not message.text.isdigit() or float(message.text) > 120,state=ProfileStatesGroup.age)
    dp.register_message_handler(load_age,state=ProfileStatesGroup.age)
    dp.register_message_handler(wrong_desc,lambda message: len(message.text) > 255,state=ProfileStatesGroup.desc)
    dp.register_message_handler(load_desc,state=ProfileStatesGroup.desc)

