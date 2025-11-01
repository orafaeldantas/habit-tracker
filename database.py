import sqlite3, logging
from flask import g, current_app

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DATABASE"])
        db.row_factory = sqlite3.Row
    return db

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            if commit:
                conn.commit()
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            return True
               
            
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        
        return False

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
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()

def create_habit_logs_table():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                habit_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                FOREIGN KEY (habit_id) REFERENCES habits(id) 
            )
        ''')

        conn.commit()
       

def insert_db_users(name, email, password):
    return execute_query("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password,))
    

def insert_db_habits(user_id, title, description):
    return execute_query('''INSERT INTO habits (user_id, title, description) VALUES (?, ?, ?)''', (user_id, title, description,))
    

def get_habits_by_user(user_id):
    return execute_query("SELECT * FROM habits WHERE user_id = ?", (user_id,), fetchall=True)


def get_habit(id):
    return execute_query("SELECT * FROM habits WHERE id = ?", (id,), fetchone=True)

    
def update_status_habits_by_id(id, status):
    return execute_query("UPDATE habits SET status = ? WHERE id = ?", (status, id,), commit=True) 


def update_habit_by_id(id, title, description):
    return execute_query("UPDATE habits SET title = ?, description = ? WHERE id = ?", (title, description, id,), commit=True) 

    
def delete_habit_by_id(id):
    return execute_query("DELETE FROM habits WHERE id = ?", (id,), commit=True) 

    
def verify_login(email):
    return execute_query("SELECT id, password, name FROM users WHERE email = ?", (email,), fetchone=True)

def counter_habits_by_user(id, status):
    if status:
        return execute_query("SELECT COUNT(*) FROM habits WHERE user_id = ? AND status = 1", (id,), fetchone=True)
    else:
        return execute_query("SELECT COUNT(*) FROM habits WHERE user_id = ? AND status = 0", (id,), fetchone=True)
 
 

def init_db():
    create_users_table()
    create_habits_table()
    create_habit_logs_table()
    logging.info('Database initialized successfully!')