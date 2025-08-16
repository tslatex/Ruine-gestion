import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///ruine_gestion.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "sslmode": "prefer",
            "application_name": "RuineGestion"
        }
    }
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-in-production")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For simplicity, tokens don't expire
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.produits_routes import produits_bp
    from routes.clients_routes import clients_bp
    from routes.ventes_routes import ventes_bp
    from routes.stocks_routes import stocks_bp
    from routes.livraisons_routes import livraisons_bp
    from routes.reservations_routes import reservations_bp
    from routes.exports_routes import exports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(produits_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(ventes_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(livraisons_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(exports_bp)
    
    with app.app_context():
        import models
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from services.auth_service import AuthService
        AuthService.create_default_user()
        
        # Démarrer le planificateur de tâches automatiques (en différé)
        def start_scheduler_delayed():
            import threading
            import time
            def delayed_start():
                time.sleep(2)  # Attendre que l'app soit complètement initialisée
                from services.scheduler_service import start_scheduler
                start_scheduler()
            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()
        
        start_scheduler_delayed()
    
    return app

app = create_app()
