from flask import Flask, g, request, render_template, redirect, url_for, session
from database import get_db, insert_db, verify_login
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# Close db - More security
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
       
    # Check if the user is logged into the session
    email_user = session.get('email_user')

    if email_user:
        return render_template('index.html')
    
    return redirect(url_for('login_user'))
   
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':

        if insert_db(request.form['name'], request.form['email'], request.form['psw']):
            return redirect(url_for('hello'))
        else:
            return "Erro ao cadastrar usuário"
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    
    if request.method == 'POST':           
        if verify_login(request.form['email'], request.form['psw']):
            session['email_user'] = request.form['email']           
            return redirect(url_for('index'))
        else:
            return 'Usuário não cadastrado!'
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout_user():
    if session.pop('email_user', None):
        return redirect(url_for('login_user'))
    else:
        print('Problemas ao sair da sessão!')
    
        
    

if __name__ == '__main__':
    app.run(debug=True)

    