from extensions import get_db

def ids_visibles(usuario_id, rol):
    if rol == 'admin':
        return None
    
    if rol == 'jefe_equipo':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE jefe_id = %s", (usuario_id,)
        )
        comerciales = [fila[0] for fila in cursor.fetchall()]
        return comerciales + [usuario_id]
    
    return [usuario_id]
