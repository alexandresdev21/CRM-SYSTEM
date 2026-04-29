from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__)

    from config import config_by_name
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes.clients import clients_bp
    from app.routes.contacts import contacts_bp
    from app.routes.campaigns import campaigns_bp
    from app.routes.interactions import interactions_bp
    from app.routes.tags import tags_bp

    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")
    app.register_blueprint(interactions_bp, url_prefix="/api/interactions")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "CRM API rodando ✅"}

    return app
