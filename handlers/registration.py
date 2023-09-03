import hashlib
import sqlite as sq
from aiogram import types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from create_bot import ProfileStatesGroup
from keyboards import *

async def start_message(message: types.Message)->None:
    start_text = "Добро пожаловать!\nДля начала нужно выполнить вход,для этого введите команду /register или /login"
    await message.answer(text = start_text,
                        reply_markup=get_keyboard())
    await message.delete()
"""
Хендлеры отмены
"""
async def cancel(message : types.Message,state :FSMContext):
    if state is None:
        return  
    await message.answer("Ты точно хочешь это сделать?\nВ случае отмены процесс регистрации прервётся и данные не сохранятся",reply_markup=choice_menu())

async def cancel_answer_one(message : types.Message,state :FSMContext):
    if message.text == 'Да':
        await message.answer("Отменил операцию",
                             reply_markup=get_keyboard())
        await state.finish()
    else:
        await message.answer("Продолжим заполнение профиля",reply_markup=get_cancel())

async def cancel_answer_two(message : types.Message,state :FSMContext):
    await message.answer("Отменил операцию",
                         reply_markup=get_keyboard())
    await state.finish()

"""
Хендлеры Регистрации
"""
async def registration(message:types.Message):
    if await sq.find_user(message.from_user.id):
        await message.reply("Ты уже зарегистрирован,для входа введи команду /login",
                            reply_markup=get_keyboard())
    else:
        await message.reply("Придумай себе пароль",
                            reply_markup=get_cancel())
        await ProfileStatesGroup.registration.set()

async def creating_profile(message:types.Message,state : FSMContext):
    password = hashlib.md5(message.text.encode()).hexdigest()
    if await sq.find_user(message.from_user.id):
        await sq.set_password(message.from_user.id,password)
        await message.answer("Смена пароля произошла успешно!")
        await message.answer("Теперь ты можешь настроить свой профиль,для этого напиши команду /create",
                             reply_markup=create_keyboard())
    else:
        await sq.create_profile_db(message.from_user.id,password)
        await message.answer("Регистрация прошла успешно,теперь ты можешь настроить свой профиль,для этого напиши команду /create",
                             reply_markup=create_keyboard())
    await state.finish()

"""
Хендлеры логина
"""

async def login(message:types.Message):
    if await sq.find_user(message.from_user.id):
        await ProfileStatesGroup.login.set()
        await message.reply("Введи пароль",
                            reply_markup=login_keyboard())
    else:
        await message.reply("Тебе нужно зарегистрироваться,для этого введи команду /registr",reply_markup=get_keyboard())
    
async def forgot_password(message: types.Message):
    await message.answer("Хочешь поменять пароль?",
                         reply_markup=choice_menu())
    await ProfileStatesGroup.login_change.set()

async def change_password(message: types.Message):
    if message.text == "Да":
        await message.answer("Введи новый пароль",
                             reply_markup=get_cancel())
        await ProfileStatesGroup.registration.set()
    elif message.text == 'Нет':
        await message.reply("Введи пароль ещё раз",
                            reply_markup=login_keyboard())
        await ProfileStatesGroup.login.set()
    else:
        await message.answer("Неверная команда",
                             reply_markup=get_cancel())
        
async def wrong_password(message:types.Message,state : FSMContext):
    password = hashlib.md5(message.text.encode()).hexdigest()
    if password != await sq.get_password(message.from_user.id):
        await message.answer("Неправильный пароль,попробуй ещё раз",
                             reply_markup=login_keyboard())
    else:
        await message.answer("Вход прошёл успешно,теперь ты можешь настроить свой профиль,для этого напиши команду /create",
                             reply_markup=create_keyboard())
        await state.finish()


def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(cancel,commands=['cancel'],state='*')
    dp.register_message_handler(cancel_answer_one,Text(equals=['Да','Нет']),state=[ProfileStatesGroup.photo,ProfileStatesGroup.name,ProfileStatesGroup.age,ProfileStatesGroup.desc])
    dp.register_message_handler(cancel_answer_two,Text(equals=['Да','Нет']),state= [ProfileStatesGroup.login,ProfileStatesGroup.registration])
    dp.register_message_handler(start_message,commands=['start'])    
    dp.register_message_handler(registration,commands=['register'],state=None)
    dp.register_message_handler(creating_profile,state=ProfileStatesGroup.registration)
    dp.register_message_handler(login,commands=['login'],state=None)
    dp.register_message_handler(forgot_password,Text(equals=('Забыл пароль')),state=ProfileStatesGroup.login)
    dp.register_message_handler(change_password,Text(equals=['Да','Нет']),state=ProfileStatesGroup.login_change)
    dp.register_message_handler(wrong_password,state=ProfileStatesGroup.login)

    
