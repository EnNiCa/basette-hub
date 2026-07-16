from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from extensions import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, password_hash, rol, activo FROM usuarios WHERE email = %s",
            (email,)
        )
        usuario = cursor.fetchone()

        if usuario and usuario['activo'] and check_password_hash(usuario['password_hash'], password):
            session.permanent = True
            session['usuario_id'] = usuario['id']
            session['nombre'] = usuario['nombre']
            session['rol'] = usuario['rol']
            return redirect(url_for('inicio'))

        flash('Email o contraseña incorrectos', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))