from flask import Flask
import extensions
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    extensions.init_app(app)
    
    return app

app = create_app()



if __name__ == '__main__':
    app.run(debug=True)