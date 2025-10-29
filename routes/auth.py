from flask import Blueprint, g, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import insert_db_users, verify_login


auth_bp = Blueprint('auth', __name__)

# === REGISTER ===   
@auth_bp.route('/register', endpoint='register', methods=['GET', 'POST'] )
def register_user():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        psw = request.form['psw']
        psw_repeat = request.form['psw-repeat']

        existing = verify_login(email)
        if existing:
            flash('Este e-mail já está cadastrado.', 'error')
            return redirect(url_for('auth.register_user'))

        if psw != psw_repeat:
            flash('As senhas digitadas são diferentes.', 'error')
            return redirect(url_for('auth.register_user'))
        
        if len(psw) < 6:
            flash('A senha precisa ter no mínimo 6 dígitos.', 'error')
            return redirect(url_for('auth.register_user'))

        if name and email and psw:
            password = generate_password_hash(psw)
            if insert_db_users(name, email, password):
                flash('Cadastro feito com sucesso.', 'success')
                return redirect(url_for('dashboard'))           
            else:
                flash('Erro ao registrar. Tente novamente mais tarde.', 'error')
                return redirect(url_for('auth.register_user'))
        else:
            flash('Preencha todos os campos necessários.', 'error')
            return redirect(url_for('auth.register_user'))
        
    return render_template('register.html')

# === LOGIN ===
@auth_bp.route('/login', methods=['GET', 'POST'])
def login_user():
    
    if request.method == 'POST': 
        user_data = verify_login(request.form['email']) 

        if user_data and check_password_hash(user_data['password'], request.form['psw']):
            session['email_user'] = request.form['email']
            session['id_user'] = user_data['id']
            session['name_user'] = user_data['name']
            flash('Login feito com sucesso.', 'success')         
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorreto.', 'error')
            return redirect(url_for('auth.login_user')) 
        
    return render_template('login.html')

# === LOGOUT ===
@auth_bp.route('/logout', methods=['GET'] )
def logout_user():
    session.pop('id_user', None)
    flash('Logout feito! Já estamos com saudades. ;)', 'success')
    return redirect(url_for('auth.login_user'))