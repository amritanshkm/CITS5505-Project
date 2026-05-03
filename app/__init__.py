from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.login'

def create_app(config_class=None):
    if config_class is None:
        from config import Config
        config_class = Config
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints or routes here
    from app import routes
    app.register_blueprint(routes.bp)

    from app import models

    # Add custom Jinja filter for Australian date formatting
    @app.template_filter('aus_date')
    def aus_date_filter(date_string):
        try:
            from datetime import datetime
            return datetime.strptime(date_string, '%Y-%m-%d').strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            return date_string

    return app
