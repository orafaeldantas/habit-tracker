import functools
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from database import insert_db_habits, get_habits_by_user, update_status_habits_by_id, get_habit, update_habit_by_id, delete_habit_by_id

habits_bp = Blueprint('habits', __name__)

# Check route login
def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'id_user' not in session:
            flash ('É necessário estar logado para acessar a página.', 'error')
            return redirect(url_for('auth.login_user'))
        return func(*args, **kwargs)
                  
    return wrapper

@habits_bp.route('/')
@login_required
def dashboard():
         
    user_id = session['id_user']
    habits = get_habits_by_user(user_id)

    return render_template('dashboard.html', habits=habits)
    
# === Add habit ===   
@habits_bp.route('/add_habit', methods=['POST', 'GET'])
@login_required
def insert_habit():
    if request.method == 'POST':

        user_id = session['id_user']

        title = request.form['title']
        description = request.form['description']

        if not title.strip():
            flash('O título do hábito é obrigatório.', 'error')
            return redirect(url_for('habits.insert_habit'))

        if insert_db_habits(user_id, title, description):

            flash('Hábito adicionado com sucesso.', 'success')
            return redirect(url_for('habits.dashboard'))
        
        flash('Erro ao adicionar hábito.', 'error')
        return redirect(url_for('habits.insert_habit'))
    
    return render_template('add_habit.html')


# === Update habit status ===
@habits_bp.route('/update_habit/<int:id>', methods=['POST'])
@login_required
def update_status_habit(id):
    if request.method == 'POST':

        habit = get_habit(id)
        if habit['user_id'] != session['id_user']:
            flash('Ação não permitida.', 'error')
            return redirect(url_for('habits.dashboard'))

        update_status_habits_by_id(id, request.form.get('status'))

        return redirect(url_for('habits.dashboard'))
       

# === Edit habit ===
@habits_bp.route('/edit_habit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_habit(id):
    if request.method == 'POST':
        title = request.form['title'] 
        description = request.form['description']

        habit = get_habit(id)
        if habit['user_id'] != session['id_user']:
            flash('Ação não permitida.', 'error')
            return redirect(url_for('habits.dashboard'))

        if not title.strip():
            flash('O título do hábito é obrigatório.', 'error')
            return redirect(url_for('habits.edit_habit', id=habit['id']))

        if update_habit_by_id(id, title, description):
            flash('Hábito atualizado com sucesso.', 'success')
            return redirect(url_for('habits.dashboard'))
        else:
            flash('Não foi possível atualizar o hábito.', 'error')
            return redirect(url_for('habits.dashboard'))
    
    habit = get_habit(id)
    return render_template('edit_habit.html', habit=habit)

# === Delete habit ===
@habits_bp.route('/delete_habit/<int:id>', methods=['POST'])
@login_required
def delete_habit(id):
    if request.method == 'POST':

        if delete_habit_by_id(id):
            flash('Hábito excluido com sucesso.', 'success')
            return redirect(url_for('habits.dashboard'))
        else:
            flash('Não foi possível excluir o hábito.', 'error')
            return redirect(url_for('habits.dashboard'))
        
# === Reports ===
@habits_bp.route('/reports', methods=['GET'])
@login_required
def reports():
    return render_template('reports.html')