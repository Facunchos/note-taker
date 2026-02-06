import os
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

from models import db, User, bcrypt

migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # --- Debug logging for Railway ---
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting app creation...")

    # --- Config ---
    database_url = os.environ.get("DATABASE_URL")
    secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")
    
    if not database_url:
        app.logger.warning("No DATABASE_URL found, using SQLite fallback")
        database_url = "sqlite:///dev.db"
    else:
        app.logger.info(f"Database URL found: {database_url[:30]}...")
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            app.logger.info("Fixed postgres:// to postgresql://")
    
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

    app.register_blueprint(auth_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(notes_bp)
    app.logger.info("App creation completed successfully!")

    # --- Root route ---
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/health")
    def health():
        try:
            # Test database connection
            with app.app_context():
                db.session.execute(db.text('SELECT 1'))
            return {"status": "ok", "database": "connected"}, 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return {"status": "error", "database": "disconnected", "error": str(e)}, 503

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
