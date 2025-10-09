from flask import Flask, g, request, render_template, redirect, url_for
from database import get_db, insert_db


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
            cur.execute("SELECT * FROM users WHERE id = ?", (1,))
            user_data = cur.fetchone()

        print(f'Usuário encontrado: {user_data}')

        return 'Hello, World!'

    except Exception as e:
        print(f'Erro ao acessar o banco: {e}')
        return 'Erro ao acessar o banco de dados.'
    
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        try:
            insert_db(request.form['name'], request.form['email'], request.form['psw'])

            return redirect(url_for('hello'))
        
        except Exception as e:
            print(f'Erro ao cadastrar: {e}')
            return "Erro ao cadastrar usuário", 500
        
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)

    