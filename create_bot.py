from aiogram import Bot,Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from aiogram.dispatcher.filters.state import StatesGroup,State

class ProfileStatesGroup(StatesGroup):
    
    registration = State()
    login = State()
    photo = State()
    name = State()
    age = State()
    desc = State()
    
    login_change = State()

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot,storage=storage)