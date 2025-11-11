#!/usr/bin/env python3
"""Main application factory for the API Gateway."""
from flask import Flask
from api.config import Config
from api.routes.notifications import notifications_bp
from api.routes.health import health_bp
from api.services.queue_service import MessageQueue
from api.services.cache_service import CacheService

def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize services
    app.queue = MessageQueue()
    app.cache = CacheService()

    # Register blueprints
    app.register_blueprint(notifications_bp)
    app.register_blueprint(health_bp)

    @app.errorhandler(404)
    def not_found(error):
        return {"success": False, 'error': 'not_found',
                'message:': 'Endpoint not found', 'meta': None}, 404

    return app