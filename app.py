from flask import Flask, request, jsonify
from flask import g
from database import get_db


app = Flask(__name__)

# Close db - More security
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", ('teste', 'teste@teste.com', '123456',))
            conn.commit()
            cur.execute("SELECT * FROM users WHERE id = ?", (1,))
            user_data = cur.fetchone()

        print(f'Usuário encontrado: {user_data}')
        return 'Hello, World!'

    except Exception as e:
        print(f'Erro ao acessar o banco: {e}')
        return 'Erro ao acessar o banco de dados.'
    
@app.route('/register', methods=['POST'])
def register_user():
    content = request.json()

    insert_db(content['name'], content['email'], content['password'])

if __name__ == '__main__':
    app.run(debug=True)

    