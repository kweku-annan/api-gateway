#!/usr/bin/env python
"""Health check route."""
from flask import Blueprint, jsonify
from api.models.response_models import HealthResponse


health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    health_data = HealthResponse.create(
        status='healthy',
        service='api-gateway',
        dependencies={
            'rabbitmq': 'not_configured',
            'redis': 'not_configured'
        }
    )

    return jsonify({health_data}), 200

