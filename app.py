from flask import Flask, render_template
import extensions
from config import Config
from auth.routes import auth_bp
from auth.decorators import login_requerido
from modules.ventas.routes import ventas_bp
from modules.usuarios.routes import usuarios_bp
from modules.liquidaciones.routes import liquidaciones_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    extensions.init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(liquidaciones_bp)
    
    @app.route("/")
    @login_requerido
    def inicio():
        return render_template('inicio.html')
    
    return app

app = create_app()



if __name__ == '__main__':
    app.run(debug=True)