from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import get_db
from auth.decorators import solo_admin

liquidaciones_bp = Blueprint('liquidaciones', __name__, url_prefix='/liquidaciones')


@liquidaciones_bp.route('/')
@solo_admin
def listar_liquidaciones():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    buscar = request.args.get('buscar', '').strip()

    sql = """
        SELECT v.id, v.nombre, v.apellidos, v.razon_social, v.tipo_cliente, v.modulo,
               v.fecha_liquidacion, v.importe_liquidar, v.fecha_descomision, v.importe_descomisionado,
               v.fecha_pago_comercial, v.importe_pago_comercial,
               v.fecha_descomision_comercial, v.importe_descomisionado_comercial,
               u.nombre AS comercial
        FROM ventas v
        JOIN usuarios u ON v.comercial_id = u.id
    """
    parametros = []

    if buscar:
        sql += """ WHERE (
            CONCAT(v.nombre, ' ', v.apellidos) LIKE %s
            OR v.razon_social LIKE %s
        )"""
        comodin = f"%{buscar}%"
        parametros += [comodin, comodin]

    sql += " ORDER BY v.id DESC"

    cursor.execute(sql, tuple(parametros))
    ventas = cursor.fetchall()

    return render_template('liquidaciones/listado.html', ventas=ventas, buscar=buscar)


@liquidaciones_bp.route('/venta/<int:venta_id>', methods=['GET', 'POST'])
@solo_admin
def editar_liquidacion_venta(venta_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, apellidos, modulo FROM ventas WHERE id = %s", (venta_id,))
    venta_basica = cursor.fetchone()
    if venta_basica is None:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('liquidaciones.listar_liquidaciones'))

    origen = request.args.get('origen') or request.form.get('origen') or url_for('liquidaciones.listar_liquidaciones')

    if request.method == 'POST':
        fecha_liquidacion = request.form.get('fecha_liquidacion') or None
        importe_liquidar = request.form.get('importe_liquidar') or None
        fecha_descomision = request.form.get('fecha_descomision') or None
        importe_descomisionado = request.form.get('importe_descomisionado') or None
        fecha_pago_comercial = request.form.get('fecha_pago_comercial') or None
        importe_pago_comercial = request.form.get('importe_pago_comercial') or None
        fecha_descomision_comercial = request.form.get('fecha_descomision_comercial') or None
        importe_descomisionado_comercial = request.form.get('importe_descomisionado_comercial') or None

        cursor.execute(
            """
            UPDATE ventas SET
                fecha_liquidacion = %s, importe_liquidar = %s,
                fecha_descomision = %s, importe_descomisionado = %s,
                fecha_pago_comercial = %s, importe_pago_comercial = %s,
                fecha_descomision_comercial = %s, importe_descomisionado_comercial = %s
            WHERE id = %s
            """,
            (
                fecha_liquidacion, importe_liquidar,
                fecha_descomision, importe_descomisionado,
                fecha_pago_comercial, importe_pago_comercial,
                fecha_descomision_comercial, importe_descomisionado_comercial,
                venta_id,
            )
        )
        db.commit()
        flash('Liquidación actualizada correctamente.', 'exito')
        return redirect(origen)

    cursor.execute("SELECT * FROM ventas WHERE id = %s", (venta_id,))
    venta = cursor.fetchone()

    return render_template('liquidaciones/editar.html', venta=venta, origen=origen)