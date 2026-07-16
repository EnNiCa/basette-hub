from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from extensions import get_db
from auth.decorators import login_requerido, solo_admin
from utils.validaciones import dni_valido

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

ROLES_VALIDOS = ('admin', 'jefe_equipo', 'comercial')


@usuarios_bp.route('/')
@solo_admin
def listar_usuarios():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT u.id, u.nombre, u.email, u.rol, u.activo, u.fecha_alta,
               j.nombre AS jefe_nombre,
               ub.fecha_baja AS fecha_baja_actual
        FROM usuarios u
        LEFT JOIN usuarios j ON u.jefe_id = j.id
        LEFT JOIN usuario_bajas ub ON u.id = ub.usuario_id AND ub.fecha_reincorporacion IS NULL
        ORDER BY u.nombre
        """
    )
    usuarios = cursor.fetchall()

    return render_template('usuarios/listado.html', usuarios=usuarios)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@solo_admin
def nuevo_usuario():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        dni = request.form.get('dni', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        rol = request.form.get('rol')
        jefe_id = request.form.get('jefe_id') or None

        errores = []
        if not nombre:
            errores.append('El nombre es obligatorio.')
        if dni and not dni_valido(dni):
            errores.append('El DNI debe tener 8 dígitos seguidos de una letra (ej: 12345678A).')
        if not email:
            errores.append('El email es obligatorio.')
        if len(password) < 8:
            errores.append('La contraseña debe tener al menos 8 caracteres.')
        if rol not in ROLES_VALIDOS:
            errores.append('El rol seleccionado no es válido.')
        if rol == 'comercial' and not jefe_id:
            errores.append('Un comercial debe tener un jefe de equipo asignado.')

        if not errores:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                errores.append('Ya existe un usuario con ese email.')

        if errores:
            for error in errores:
                flash(error, 'error')
            cursor.execute("SELECT id, nombre FROM usuarios WHERE rol = 'jefe_equipo' AND activo = TRUE")
            jefes = cursor.fetchall()
            return render_template('usuarios/nuevo.html', jefes=jefes)

        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuarios (nombre, dni, email, password_hash, rol, jefe_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, dni or None, email, password_hash, rol, jefe_id)
)
        db.commit()
        flash('Usuario creado correctamente.', 'exito')
        return redirect(url_for('usuarios.listar_usuarios'))

    cursor.execute("SELECT id, nombre FROM usuarios WHERE rol = 'jefe_equipo' AND activo = TRUE")
    jefes = cursor.fetchall()
    return render_template('usuarios/nuevo.html', jefes=jefes)

@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@solo_admin
def editar_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()
    if usuario is None:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('usuarios.listar_usuarios'))

    cursor.execute("SELECT id, nombre FROM usuarios WHERE rol = 'jefe_equipo' AND activo = TRUE AND id != %s", (usuario_id,))
    jefes = cursor.fetchall()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        dni = request.form.get('dni', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        rol = request.form.get('rol')
        jefe_id = request.form.get('jefe_id') or None
        activo_nuevo = request.form.get('activo') == 'on'
        activo_anterior = usuario['activo']

        errores = []
        if not nombre:
            errores.append('El nombre es obligatorio.')
        if dni and not dni_valido(dni):
            errores.append('El DNI debe tener 8 dígitos seguidos de una letra (ej: 12345678A).')
        if not email:
            errores.append('El email es obligatorio.')
        if password and len(password) < 8:
            errores.append('La contraseña debe tener al menos 8 caracteres.')
        if rol not in ROLES_VALIDOS:
            errores.append('El rol seleccionado no es válido.')
        if rol == 'comercial' and not jefe_id:
            errores.append('Un comercial debe tener un jefe de equipo asignado.')

        if not errores:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, usuario_id))
            if cursor.fetchone():
                errores.append('Ya existe otro usuario con ese email.')

        if errores:
            for error in errores:
                flash(error, 'error')
            usuario.update(request.form.to_dict())
            usuario['id'] = usuario_id
            return render_template('usuarios/editar.html', usuario=usuario, jefes=jefes)

        if password:
            password_hash = generate_password_hash(password)
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, dni=%s, email=%s, rol=%s, jefe_id=%s, activo=%s, password_hash=%s WHERE id=%s",
                (nombre, dni or None, email, rol, jefe_id, activo_nuevo, password_hash, usuario_id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, dni=%s, email=%s, rol=%s, jefe_id=%s, activo=%s WHERE id=%s",
                (nombre, dni or None, email, rol, jefe_id, activo_nuevo, usuario_id)
            )

        if activo_anterior and not activo_nuevo:
            cursor.execute(
                "INSERT INTO usuario_bajas (usuario_id, fecha_baja) VALUES (%s, CURDATE())",
                (usuario_id,)
            )
        elif not activo_anterior and activo_nuevo:
            cursor.execute(
                """
                UPDATE usuario_bajas SET fecha_reincorporacion = CURDATE()
                WHERE usuario_id = %s AND fecha_reincorporacion IS NULL
                ORDER BY fecha_baja DESC LIMIT 1
                """,
                (usuario_id,)
            )

        db.commit()
        flash('Usuario actualizado correctamente.', 'exito')
        return redirect(url_for('usuarios.listar_usuarios'))

    return render_template('usuarios/editar.html', usuario=usuario, jefes=jefes)