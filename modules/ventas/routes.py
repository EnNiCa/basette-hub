from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from extensions import get_db
from auth.decorators import login_requerido
from auth.permisos import ids_visibles
from utils.validaciones import dni_valido, telefono_valido, cups_valido, iban_valido

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
@login_requerido
def listar_ventas():
    db =get_db()
    cursor = db.cursor(dictionary=True)
    
    visibles = ids_visibles(session['usuario_id'], session['rol'])
    
    sql = """
        SELECT v.id, v.nombre, v.apellidos, v.modulo, v.estado, v.fecha_venta,
        c.nombre AS compania, t.nombre AS tarifa, u.nombre AS comercial
        FROM ventas v
        JOIN companias c ON v.compania_id = c.id
        JOIN tarifas t ON v.tarifa_id = t.id
        JOIN usuarios u ON v.comercial_id = u.id
    """
    
    parametros = ()
    if visibles is not None:
        placeholders = ','.join(['%s'] * len(visibles))
        sql += f" WHERE v.comercial_id IN ({placeholders})"
        parametros = tuple(visibles)
        
    sql += " ORDER BY v.fecha_venta DESC"
        
    cursor.execute(sql, parametros)
    ventas = cursor.fetchall()
        
    return render_template('ventas/listado.html', ventas=ventas)    

@ventas_bp.route('/nueva', methods=['GET', 'POST'])
@login_requerido
def nueva_venta():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        dni = request.form.get('dni', '').strip().upper()
        telefono = request.form.get('telefono', '').strip()
        cups = request.form.get('cups', '').strip().upper()
        numero_cuenta = request.form.get('numero_cuenta', '').strip().upper()

        errores = []
        if not dni_valido(dni):
            errores.append('El DNI debe tener 8 dígitos seguidos de una letra (ej: 12345678A).')
        if telefono and not telefono_valido(telefono):
            errores.append('El teléfono debe tener exactamente 9 dígitos.')
        if not cups_valido(cups):
            errores.append('El CUPS no tiene un formato válido (ej: ES0021000005311232MT).')
        if not iban_valido(numero_cuenta):
            errores.append('El número de cuenta no tiene un formato IBAN válido.')

        if errores:
            for error in errores:
                flash(error)
            cursor.execute("SELECT id, nombre FROM companias")
            companias = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM tarifas WHERE vigente = TRUE")
            tarifas = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM canales")
            canales = cursor.fetchall()
            return render_template('ventas/nueva.html', companias=companias, tarifas=tarifas, canales=canales)
        
        cursor.execute(
            """
            INSERT INTO ventas
                (comercial_id, modulo, compania_id, tarifa_id, canal_id,
                 nombre, apellidos, dni, cups, telefono, email, numero_cuenta, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['usuario_id'],
                request.form.get('modulo'),
                request.form.get('compania_id'),
                request.form.get('tarifa_id'),
                request.form.get('canal_id') or None,
                request.form.get('nombre'),
                request.form.get('apellidos'),
                request.form.get('dni'),
                request.form.get('cups'),
                request.form.get('telefono'),
                request.form.get('email'),
                request.form.get('numero_cuenta'),
                'pendiente_carga',
            )
        )
        db.commit()
        return redirect(url_for('ventas.listar_ventas'))

    cursor.execute("SELECT id, nombre FROM companias")
    companias = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM tarifas WHERE vigente = TRUE")
    tarifas = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM canales")
    canales = cursor.fetchall()

    return render_template(
        'ventas/nueva.html',
        companias=companias,
        tarifas=tarifas,
        canales=canales
    )