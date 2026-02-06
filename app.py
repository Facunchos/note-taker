import os
from datetime import datetime
from flask import Flask, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

from models import db, User, bcrypt, DiceRoll, InitiativeSession, InitiativeEntry

migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # --- Debug logging for Railway ---
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting app creation...")

    # --- Version Info ---
    def get_version():
        try:
            with open("VERSION", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return os.environ.get("APP_VERSION", "2.0.0")

    # Make version available in all templates
    @app.context_processor
    def inject_version():
        return {"version": get_version()}

    # --- Config ---
    database_url = os.environ.get("DATABASE_URL")
    secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")
    
    app.logger.info(f"SECRET_KEY present: {'Yes' if secret_key != 'dev-fallback-key' else 'No (using fallback)'}")
    
    if not database_url:
        app.logger.warning("No DATABASE_URL found, using SQLite fallback")
        database_url = "sqlite:///dev.db"
    else:
        app.logger.info(f"Database URL found: {database_url[:50]}...")
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            app.logger.info("Fixed postgres:// to postgresql://")
        
        # Add connection pool settings for Railway
        if "postgresql://" in database_url and "?" not in database_url:
            database_url += "?sslmode=require"
            app.logger.info("Added SSL mode requirement")
    
    app.logger.info(f"Secret key present: {'Yes' if secret_key else 'No'}")

    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Init extensions ---
    app.logger.info("Initializing database...")
    try:
        db.init_app(app)
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database init failed: {e}")
        raise
        
    app.logger.info("Initializing migrate...")
    migrate.init_app(app, db)
    
    # DON'T try to connect to DB during startup - let it fail gracefully later
    app.logger.info("Database initialization deferred until first request")
    
    app.logger.info("Initializing login manager...")
    login_manager.init_app(app)
    app.logger.info("Initializing bcrypt...")
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Register blueprints ---
    app.logger.info("Registering blueprints...")
    from routes.auth import auth_bp
    from routes.tables import tables_bp
    from routes.notes import notes_bp
    from routes.dice import dice_bp
    from routes.initiative import initiative_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(dice_bp)
    app.register_blueprint(initiative_bp)
    app.logger.info("App creation completed successfully!")

    # Add before_request handler to ensure DB is ready
    @app.before_request
    def before_request():
        # Skip DB init for health checks and static files
        if request.endpoint in ['health', 'db_health', 'db_init', 'db_tables'] or request.path.startswith('/static'):
            return
        
        # For other routes, try to ensure DB is ready (only once)
        if not hasattr(app, '_db_checked'):
            try:
                ensure_database_ready()
                app._db_checked = True
            except Exception as e:
                app.logger.warning(f"DB initialization failed, but continuing: {e}")
                app._db_checked = True  # Don't retry on every request

    # Database initialization helper
    def ensure_database_ready():
        """Initialize database tables if they don't exist"""
        try:
            # Test if tables exist
            db.session.execute(db.text('SELECT 1 FROM users LIMIT 1'))
            app.logger.info("Database schema verified")
            return True
        except Exception as e:
            app.logger.warning(f"Database schema not found: {e}")
            try:
                app.logger.info("Creating database tables...")
                db.create_all()
                app.logger.info("Database tables created successfully")
                return True
            except Exception as create_error:
                app.logger.error(f"Failed to create tables: {create_error}")
                return False

    # --- Root route ---
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200
    
    @app.route("/db-health")
    def db_health():
        try:
            # Test database connection
            with app.app_context():
                db.session.execute(db.text('SELECT 1'))
                db.session.commit()
            return {"status": "ok", "database": "connected"}, 200
        except Exception as e:
            app.logger.error(f"DB Health check failed: {e}")
            return {"status": "error", "database": "disconnected", "error": str(e)}, 503

    @app.route("/db-init")
    def db_init():
        """Manually initialize database tables"""
        try:
            if ensure_database_ready():
                return {"status": "ok", "message": "Database initialized"}, 200
            else:
                return {"status": "error", "message": "Database initialization failed"}, 500
        except Exception as e:
            return {"status": "error", "error": str(e)}, 500

    @app.route("/db-tables")
    def db_tables():
        try:
            with app.app_context():
                # Get table names from the database
                if 'postgresql' in database_url:
                    result = db.session.execute(db.text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                    ))
                else:  # SQLite
                    result = db.session.execute(db.text(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ))
                tables = [row[0] for row in result]
                return {"status": "ok", "tables": tables}, 200
        except Exception as e:
            app.logger.error(f"DB Tables check failed: {e}")
            return {"status": "error", "error": str(e)}, 503

    # --- Error handlers ---
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return {"error": "Internal server error", "details": str(error)}, 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return {"error": "Something went wrong", "details": str(e)}, 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
