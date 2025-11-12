#!/usr/bin/env python
"""Health check route."""
from flask import Blueprint, jsonify, current_app
from api.models.response_models import HealthResponse


health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Check RabbitMQ status
    rabbitmq_status = 'disconnected'
    if hasattr(current_app, 'queue_service') and current_app.queue_service:
        if current_app.queue_service.is_connected():
            rabbitmq_status = 'connected'

    # Check Redis status
    redis_status = 'disconnected'
    if hasattr(current_app, 'cache_service') and current_app.cache_service:
        if current_app.cache_service.is_connected():
            redis_status = 'connected'

    health_data = HealthResponse.create(
        status='healthy',
        service='api-gateway',
        dependencies={
            'rabbitmq': rabbitmq_status,
            'redis': redis_status
        }
    )
    return jsonify(health_data), 200

