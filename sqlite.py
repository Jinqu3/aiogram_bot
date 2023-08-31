import sqlite3
from config import path_db

async def db_start():
    global db,cur

    db = sqlite3.connect(path_db)
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT PRIMARY KEY,photo TEXT,age TEXT,description TEXT,name TEXT,password TEXT)")
    
    db.commit()

async def create_profile_db(user_id,password):
    if not await find_user(user_id):
        cur.execute("INSERT INTO profile VALUES(?,?,?,?,?,?)",(user_id,'','','','',password))
        db.commit()

async def get_password(user_id):
    return cur.execute("SELECT password FROM profile WHERE user_id == ?",(user_id,)).fetchone()[0]

async def set_password(user_id,new_password):
    cur.execute("UPDATE profile SET password = ? WHERE user_id == ?",(new_password,user_id,))

async def find_user(user_id):
    return cur.execute("SELECT user_id FROM profile WHERE user_id == ?",(user_id,)).fetchone()
    
async def edit_profile_db(data,user_id):
    cur.execute("UPDATE profile SET photo = ? ,age = ? ,description = ? ,name = ? WHERE user_id == ?",
                (data['photo'],data['age'],data['desc'],data['name'],user_id))
    db.commit()
