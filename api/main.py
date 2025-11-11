#!/usr/bin/env python3
"""Flask application factory."""

from flask import Flask, jsonify
from api.config import config
from api.routes.health import health_bp
from api.models.response_models import StandardResponse
from api.routes.notifications import notifications_bp


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        response = StandardResponse.error(
            error='bad_request',
            message='The request is malformed or invalid'
        )
        return jsonify(response), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors"""
        response = StandardResponse.error(
            error='unauthorized',
            message='Authentication is required to access this resource'
        )
        return jsonify(response), 401

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        response = StandardResponse.error(
            error='not_found',
            message='The requested endpoint does not exist'
        )
        return jsonify(response), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        response = StandardResponse.error(
            error='method_not_allowed',
            message='The HTTP method is not allowed for this endpoint'
        )
        return jsonify(response), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        response = StandardResponse.error(
            error='internal_error',
            message='An internal server error occurred'
        )
        return jsonify(response), 500

    return app