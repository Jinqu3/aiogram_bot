from aiogram import executor
import sqlite as sq
from create_bot import dp

async def on_startup(_):
    await sq.db_start()

from handlers import registration,profile

registration.register_handlers_registration(dp)
profile.register_handlers_profile(dp)

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True,on_startup=on_startup)
