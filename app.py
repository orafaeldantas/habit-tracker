import secrets, logging, os, functools
from flask import Flask, g, request, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from database import init_db, insert_db_users, verify_login, insert_db_habits, get_habits_by_user, get_id_user, update_status_habits_by_id

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["DATABASE"] = os.path.join(BASE_DIR, "habit-tracker.db")

logging.basicConfig(level=logging.INFO)

with app.app_context():
    init_db()
    #insert_db_habits(1, 'Teste de titulo 2', 'Teste de descrição 2')


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'id_user' not in session:
            flash ('É necessário estar logado para acessar a página!')
            return redirect(url_for('login_user'))
        return func(*args, **kwargs)
                  
    return wrapper

# Close db - More security
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logging.info("Conexão com o banco encerrada.")


@app.route('/')
@login_required
def dashboard():
       
    email_user = session.get('email_user')
    
    user_id = get_id_user(email_user)
    habits = get_habits_by_user(user_id)

    return render_template('dashboard.html', habits=habits)
    
   

@app.route('/add_habit', methods=['POST', 'GET'])
@login_required
def insert_habit():
    if request.method == 'POST':

        user_id = get_id_user(session.get('email_user'))

        title = request.form['title']
        description = request.form['description']

        if title and insert_db_habits(user_id, title, description):

            flash('Hábito adicionado com sucesso!')
            return redirect(url_for('dashboard'))
        
        flash('Erro ao adicionar hábito!', 'error')
        return redirect(url_for('insert_habit'))
    
    return render_template('add_habit.html')


@app.route('/update_habit/<int:id>', methods=['POST'])
@login_required
def update_status_habit(id):
    if request.method == 'POST':

        update_status_habits_by_id(id, request.form.get('status'))

        return redirect(url_for('dashboard'))

# === REGISTER ===   
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':

        if insert_db_users(request.form['name'], request.form['email'], request.form['psw']):
            return redirect(url_for('dashboard'))           
        else:
            return "Erro ao cadastrar usuário"
        
    return render_template('register.html')

# === LOGIN ===
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    
    if request.method == 'POST': 
        user_data = verify_login(request.form['email']) 

        if user_data and user_data['password'] == request.form['psw']:
            session['email_user'] = request.form['email']
            session['id_user'] = user_data['id']         
            return redirect(url_for('dashboard'))
        else:
            return 'Usuário não cadastrado!'
        
    return render_template('login.html')

# === LOGOUT ===
@login_required
@app.route('/logout', methods=['GET'])
def logout_user():
    session.pop('id_user', None)
    return redirect(url_for('login_user'))

    
        
if __name__ == '__main__':
    app.run(debug=True)

    