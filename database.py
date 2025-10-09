import sqlite3
from flask import g

DATABASE = 'habit-tracker.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def insert_db(name, email, password):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                        (name, email, password,))

        return True

    except sqlite3.Error as e:
        print(f'Erro SQLite: {e}')
        return False
    
def verify_login(email, password):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = ? AND password = ?)", (email, password,))
            user_exists = cur.fetchone()[0]

            return user_exists

    except sqlite3.Error as e:
        print(f'Erro SQLite: {e}')
        return False  
