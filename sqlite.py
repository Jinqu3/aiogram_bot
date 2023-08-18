import sqlite3

async def db_start():
    global db,cur

    db = sqlite3.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id TEXT PRIMARY KEY,photo TEXT,age TEXT,description TEXT,name TEXT)")
    
    db.commit()

async def create_profile_db(user_id):
    user = cur.execute("SELECT user_id FROM profile WHERE user_id == ?",(user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?,?,?,?,?)",(user_id,'','','',''))
        db.commit()
    
async def edit_profile_db(data,user_id):
    cur.execute("UPDATE profile SET photo = ? ,age = ? ,description = ? ,name = ? WHERE user_id == ?",
                (data['photo'],data['age'],data['desc'],data['name'],user_id))
    db.commit()