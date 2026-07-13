from flask import Blueprint, render_template, session
from extensions import get_db
from auth.decorators import login_requerido
from auth.permisos import ids_visibles

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