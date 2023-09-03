from aiogram.types import ReplyKeyboardMarkup,KeyboardButton


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
    kb.add(KeyboardButton("/register"),KeyboardButton("/login")).add(KeyboardButton("/cancel"))
    return kb

def login_keyboard()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Забыл пароль"),KeyboardButton("/cancel"))
    return kb

def choice_menu()->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Да"),KeyboardButton("Нет"))
    return kb