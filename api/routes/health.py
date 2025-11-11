#!/usr/bin/env python
"""Health check route."""
from flask import Blueprint, current_app
from api.models.response_models import StandardResponse

health_bp = Blueprint('health', __name__)

@health_bp.route('/notifications/health', methods=['GET'])
def health_check():
    """Service health check endpoint"""
    health_service = {
        'status': 'healthy',
        'services': {
            'rabbitmq': current_app.queue.check_connection(),
            'redis': current_app.cache.check_connection()
        }
    }

    return StandardResponse.success(data=health_service, message="Health check successful"), 200