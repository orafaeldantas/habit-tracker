import logging, os, functools
from flask import Flask, g, request, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from database import init_db, insert_db_users, verify_login, insert_db_habits, get_habits_by_user, update_status_habits_by_id, get_habit, update_habit_by_id, delete_habit_by_id
from routes.auth import auth_bp


load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["DATABASE"] = os.path.join(BASE_DIR, "habit-tracker.db")

app.register_blueprint(auth_bp)

with app.app_context():
    init_db()

# Check route login
def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'id_user' not in session:
            flash ('É necessário estar logado para acessar a página.', 'error')
            return redirect(url_for('auth.login_user'))
        return func(*args, **kwargs)
                  
    return wrapper

# Close db - More security
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logging.info("Database connection closed.")


@app.route('/')
@login_required
def dashboard():
       
    email_user = session.get('email_user')
    
    user_id = session['id_user']
    habits = get_habits_by_user(user_id)

    return render_template('dashboard.html', habits=habits)
    
   
@app.route('/add_habit', methods=['POST', 'GET'])
@login_required
def insert_habit():
    if request.method == 'POST':

        user_id = session['id_user']

        title = request.form['title']
        description = request.form['description']

        if not title.strip():
            flash('O título do hábito é obrigatório.', 'error')
            return redirect(url_for('insert_habit'))

        if title and insert_db_habits(user_id, title, description):

            flash('Hábito adicionado com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Erro ao adicionar hábito.', 'error')
        return redirect(url_for('insert_habit'))
    
    return render_template('add_habit.html')


# === Update habit status ===
@app.route('/update_habit/<int:id>', methods=['POST'])
@login_required
def update_status_habit(id):
    if request.method == 'POST':

        update_status_habits_by_id(id, request.form.get('status'))

        return redirect(url_for('dashboard'))
       

# === Edit habit ===
@app.route('/edit_habit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_habit(id):
    if request.method == 'POST':
        title = request.form['title'] 
        description = request.form['description']

        if not title.strip():
            habit = get_habit(id)
            flash('O título do hábito é obrigatório.', 'error')
            return redirect(url_for('edit_habit', id=habit['id']))

        if update_habit_by_id(id, title, description):
            flash('Hábito atualizado com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Não foi possível atualizar o hábito.', 'error')
            return redirect(url_for('dashboard'))
    
    habit = get_habit(id)
    return render_template('edit_habit.html', habit=habit)

# === Delete habit ===
@app.route('/delete_habit/<int:id>', methods=['POST'])
@login_required
def delete_habit(id):
    if request.method == 'POST':

        if delete_habit_by_id(id):
            flash('Hábito excluido com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Não foi possível excluir o hábito.', 'error')
            return redirect(url_for('dashboard'))


      
if __name__ == '__main__':
    app.run(debug=True)

    