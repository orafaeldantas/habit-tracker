import sqlite3
from flask import g, current_app


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DATABASE"])
        db.row_factory = sqlite3.Row
    return db

def create_users_table():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def create_habits_table():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP,
                status INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
       

def insert_db_users(name, email, password):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                        (name, email, password,))

        return True

    except sqlite3.Error as e:
        print(f'Error SQLite: {e}')
        return False
    
def insert_db_habits(user_id, title, description):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO habits (user_id, title, description) VALUES (?, ?, ?)",
                        (user_id, title, description,))
            
            return True
        
    except sqlite3.Error as e:
        print(f'Error SQLite: {e}')

        return False
    

def get_habits_by_user(user_id):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,)) 
            result = cur.fetchall()
        
        return result

    except sqlite3.Error as e:
        print(f'Error SQLite: {e}')
        return False
    
def update_status_habits_by_id(id, status):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE habits SET status = ? WHERE id = ?", (status, id,)) 
            conn.commit()
            
        return True

    except sqlite3.Error as e:
        print(f'Error SQLite: {e}')
        return False
    
def verify_login(email):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password, name FROM users WHERE email = ?", (email,))
            user_exists = cur.fetchone()

            return user_exists

    except sqlite3.Error as e:
        print(f'Erro SQLite: {e}')
        return False  


def init_db():
    create_users_table()
    create_habits_table()
    print('Database initialized successfully!')