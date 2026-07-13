from functools import wraps
from flask import session, redirect, url_for, abort

def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def solo_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('rol') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper