import sqlite3, logging
import locale
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

def create_daily_reset_table():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS daily_reset (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reset_date DATE NOT NULL
            )
        ''')

        conn.commit() 

def create_daily_logs_table():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(''' 
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                total_habits INTEGER NOT NULL,
                completed_habits INTEGER NOT NULL,
                pending_habits INTEGER NOT NULL,
                completion_rate REAL NOT NULL, 
                weekday TEXT NOT NULL   
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

  
# === Daily Reset Functions ===

def get_last_daily_reset():
    return execute_query("SELECT reset_date FROM daily_reset ORDER BY id DESC LIMIT ?", (1,), fetchone=True)


def insert_daily_reset(date):
     return execute_query("INSERT INTO daily_reset (reset_date) VALUES (?)", (date,), commit=True)

# ============================= 

# === Log ===
# Action -> 'created', 'updated', 'deleted', 'completed'

def insert_log(user_id, habit_id, action):
    return execute_query('''INSERT INTO habit_logs(user_id, habit_id, action) VALUES (?, ?, ?)''', (user_id, habit_id, action,))

# ============================= 

# === Reports Filter ===

def filter_report(filter, user_id):
    filter_value = f'-{filter} day'

    data = {}

    data['total_habits'] = execute_query("SELECT SUM(total_habits) AS new_total_habits FROM daily_logs WHERE DATE(date) >= DATE('now', ?) and user_id = ?", (filter_value, user_id,), fetchone=True)[0]
    data['completed_habits'] = execute_query("SELECT SUM(completed_habits) AS new_completed_habits FROM daily_logs WHERE DATE(date) >= DATE('now', ?) and user_id = ?", (filter_value, user_id,), fetchone=True)[0]
    data['pending_habits'] = execute_query("SELECT SUM(pending_habits) AS new_pending_habits FROM daily_logs WHERE DATE(date) >= DATE('now', ?) and user_id = ?", (filter_value, user_id,), fetchone=True)[0]
    data['completion_rate'] = (round((data['completed_habits']/data['total_habits'])*100,2))

    weekday = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for day in range(0, 7):      
        data[weekday[day]] = execute_query("SELECT AVG(completion_rate) FROM daily_logs WHERE DATE(date) >= DATE('now', ?) and user_id = ? and weekday = ?", (filter_value, user_id, day), fetchone=True)[0]

    return data

# === Daily Log ===

def insert_daily_log(user_id):

    total_habits = execute_query("SELECT COUNT(*) FROM habits WHERE user_id = ?", (user_id,), fetchone=True)[0]

    # completed_habits = execute_query('''SELECT COUNT(*) FROM habit_logs WHERE DATE(timestamp) >= DATE('now', '-1 day') and
    #                                 user_id = ? and action = 'completed' ''', (user_id,), fetchone=True)[0]

    completed_habits = execute_query('''SELECT COUNT(*) FROM habits WHERE user_id = ? and status = 1''', (user_id,), fetchone=True)[0]

    pending_habits = total_habits - completed_habits

    completion_rate = round((completed_habits / total_habits) * 100 if total_habits > 0 else 0, 2)

    
    return execute_query('''INSERT INTO daily_logs(user_id, date, total_habits, completed_habits, pending_habits, completion_rate, weekday) 
                          VALUES (?, DATE('now', '-1 day'), ?, ?, ?, ?, strftime('%w', DATE('now', '-1 day')))
                         ''', (user_id, total_habits, completed_habits, pending_habits, completion_rate,), commit=True)

# ============================= 



def init_db():
    create_users_table()
    create_habits_table()
    create_habit_logs_table()
    create_daily_reset_table()
    create_daily_logs_table()
    logging.info('Database initialized successfully!')