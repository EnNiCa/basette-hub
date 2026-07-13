import mysql.connector
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**current_app.config['DB_CONFIG'])
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
def init_app(app):
    app.teardown_appcontext(close_db)