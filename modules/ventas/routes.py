import os
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app, abort
from extensions import get_db
from auth.decorators import login_requerido, solo_admin
from auth.permisos import ids_visibles
from utils.validaciones import dni_valido, telefono_valido, cups_valido, iban_valido, cp_valido
from werkzeug.utils import secure_filename

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

MODULOS_VALIDOS = ('energia', 'alarmas', 'telefonia', 'placas_solares')
ESTADOS_VALIDOS = ('nulo', 'pendiente_carga', 'pendiente_firma', 'scoring',
                   'activacion', 'activa', 'incidencia', 'baja')

CATEGORIAS_ARCHIVO = ('dni', 'certificado_bancario', 'escritura', 'justo_titulo',
                      'cif', 'facturas', 'acta_comunidad', 'otros')


@ventas_bp.route('/general')
@login_requerido
def listar_ventas_general():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    visibles = ids_visibles(session['usuario_id'], session['rol'])

    sql = """
        SELECT v.*, c.nombre AS compania, t.nombre AS tarifa, u.nombre AS comercial,
               ca.nombre AS canal, b.fecha_baja AS fecha_baja
        FROM ventas v
        JOIN companias c ON v.compania_id = c.id
        JOIN tarifas t ON v.tarifa_id = t.id
        JOIN usuarios u ON v.comercial_id = u.id
        LEFT JOIN canales ca ON v.canal_id = ca.id
        LEFT JOIN bajas b ON v.id = b.venta_id
    """

    parametros = []
    if visibles is not None:
        placeholders = ','.join(['%s'] * len(visibles))
        sql += f" WHERE v.comercial_id IN ({placeholders})"
        parametros = visibles

    sql += " ORDER BY v.id DESC"

    cursor.execute(sql, tuple(parametros))
    ventas = cursor.fetchall()

    es_admin = session['rol'] == 'admin'

    return render_template('ventas/listado_general.html', ventas=ventas, es_admin=es_admin)

@ventas_bp.route('/')
@login_requerido
def listar_ventas():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    visibles = ids_visibles(session['usuario_id'], session['rol'])
    
    modulo_filtro = request.args.get('modulo', 'energia')
    if modulo_filtro not in MODULOS_VALIDOS:
        modulo_filtro = 'energia'

    sql = """
        SELECT v.*, c.nombre AS compania, t.nombre AS tarifa, u.nombre AS comercial,
               ca.nombre AS canal, b.fecha_baja AS fecha_baja
        FROM ventas v
        JOIN companias c ON v.compania_id = c.id
        JOIN tarifas t ON v.tarifa_id = t.id
        JOIN usuarios u ON v.comercial_id = u.id
        LEFT JOIN canales ca ON v.canal_id = ca.id
        LEFT JOIN bajas b ON v.id = b.venta_id
        WHERE v.modulo = %s
    """

    parametros = [modulo_filtro]
    if visibles is not None:
        placeholders = ','.join(['%s'] * len(visibles))
        sql += f" AND v.comercial_id IN ({placeholders})"
        parametros += visibles

    sql += " ORDER BY v.id DESC"

    cursor.execute(sql, tuple(parametros))
    ventas = cursor.fetchall()

    es_admin = session['rol'] == 'admin'

    return render_template(
        f'ventas/listado_{modulo_filtro}.html',
        ventas=ventas,
        es_admin=es_admin,
        modulo_actual=modulo_filtro
    )
    
@ventas_bp.route('/<int:venta_id>/estado', methods=['POST'])
@solo_admin
def actualizar_estado(venta_id):
    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in ESTADOS_VALIDOS:
        flash('Estado no válido.')
        return redirect(url_for('ventas.listar_ventas'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ventas SET estado = %s WHERE id = %s",
        (nuevo_estado, venta_id)
    )
    db.commit()

    flash('Estado actualizado correctamente.')

    modulo_actual = request.form.get('modulo_actual', 'energia')
    return redirect(url_for('ventas.listar_ventas', modulo=modulo_actual))

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
        cp = request.form.get('cp', '').strip()
        modulo = request.form.get('modulo')

        errores = []
        if not dni_valido(dni):
            errores.append('El DNI debe tener 8 dígitos seguidos de una letra (ej: 12345678A).')
        if telefono and not telefono_valido(telefono):
            errores.append('El teléfono debe tener exactamente 9 dígitos.')
        if not cups_valido(cups):
            errores.append('El CUPS no tiene un formato válido (ej: ES0021000005311232MT).')
        if not iban_valido(numero_cuenta):
            errores.append('El número de cuenta no tiene un formato IBAN válido.')
        if not cp_valido(cp):
            errores.append('El código postal debe tener 5 dígitos.')

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
                (comercial_id, modulo, tipo_energia, compania_id, tarifa_id, canal_id,
                 nombre, apellidos, direccion, cp, dni, cups, telefono, email,
                 numero_cuenta, observaciones, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['usuario_id'],
                modulo,
                request.form.get('tipo_energia') or None,
                request.form.get('compania_id'),
                request.form.get('tarifa_id'),
                request.form.get('canal_id') or None,
                request.form.get('nombre'),
                request.form.get('apellidos'),
                request.form.get('direccion'),
                cp or None,
                dni,
                cups or None,
                telefono or None,
                request.form.get('email'),
                numero_cuenta or None,
                request.form.get('observaciones'),
                'pendiente_carga',
            )
        )
        db.commit()
        return redirect(url_for('ventas.listar_ventas', modulo=modulo))

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
    
@ventas_bp.route('/<int:venta_id>/archivos')
@login_requerido
def ver_archivos(venta_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, comercial_id, modulo, nombre, apellidos FROM ventas WHERE id = %s", (venta_id,))
    venta = cursor.fetchone()
    if venta is None:
        abort(404)

    visibles = ids_visibles(session['usuario_id'], session['rol'])
    if visibles is not None and venta['comercial_id'] not in visibles:
        abort(403)

    cursor.execute(
        "SELECT id, categoria, nombre_archivo, fecha_subida FROM venta_archivos WHERE venta_id = %s",
        (venta_id,)
    )
    archivos_todos = cursor.fetchall()

    archivos_por_categoria = {cat: [] for cat in CATEGORIAS_ARCHIVO}
    for archivo in archivos_todos:
        archivos_por_categoria[archivo['categoria']].append(archivo)

    return render_template(
        'ventas/archivos_adjuntos.html',
        venta=venta,
        archivos_por_categoria=archivos_por_categoria
    )


@ventas_bp.route('/<int:venta_id>/archivo', methods=['POST'])
@login_requerido
def subir_archivo(venta_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT comercial_id FROM ventas WHERE id = %s", (venta_id,))
    venta = cursor.fetchone()
    if venta is None:
        abort(404)

    visibles = ids_visibles(session['usuario_id'], session['rol'])
    if visibles is not None and venta['comercial_id'] not in visibles:
        abort(403)

    categoria = request.form.get('categoria')
    if categoria not in CATEGORIAS_ARCHIVO:
        flash('Categoría de archivo no válida.')
        return redirect(url_for('ventas.ver_archivos', venta_id=venta_id))

    archivos = request.files.getlist('archivo')

    if not archivos or archivos[0].filename == '':
        flash('No se ha seleccionado ningún archivo.')
        return redirect(url_for('ventas.ver_archivos', venta_id=venta_id))

    for archivo in archivos:
        if archivo.filename == '':
            continue
        nombre_seguro = secure_filename(archivo.filename)
        nombre_final = f"{venta_id}_{categoria}_{nombre_seguro}"
        ruta_completa = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_final)
        archivo.save(ruta_completa)

        cursor.execute(
            "INSERT INTO venta_archivos (venta_id, categoria, nombre_archivo, ruta_archivo) VALUES (%s, %s, %s, %s)",
            (venta_id, categoria, archivo.filename, ruta_completa)
        )

    db.commit()
    flash('Archivo(s) subido(s) correctamente.')
    return redirect(url_for('ventas.ver_archivos', venta_id=venta_id))