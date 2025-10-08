import sqlite3
from flask import g

DATABASE = 'habit-tracker.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def insert_db(name, email, password):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password,))
            conn.commit()

        return 'Dados inseridos com sucesso!'

    except Exception as e:
        print(f'Erro ao acessar o banco: {e}')
        return 'Erro ao acessar o banco de dados.'
