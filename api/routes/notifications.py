#!/usr/bin/env python
"""Core endpoint for notifications requests and responses management."""
from flask import Blueprint, request, jsonify, current_app
from api.middleware.auth import require_auth
from api.middleware.rate_limiter import rate_limit
from api.models.request_models import NotificationRequest
from api.models.request_models import StandardResponse

from api.utils.validators import validate_notification_data

# Create notification blueprint
notifications_bp = Blueprint('notifications', __name__)

# Endpoint to send email notification
@require_auth
@rate_limit
@notifications_bp.route('/notifications/email', methods=['POST'])
def send_email():
    """Send email notification."""
    data = request.get_json()

    # Validate for required fields
    validate_error = validate_notification_data(data)
    if validate_error:
        return jsonify(
            StandardResponse.error(error_code=400, message="Validation error!", error_message=validate_error)
        ), 200

    # Process valid request and response
    try:
        notification_id = current_app.queue.publish_notification(
            notification_type='email',
            user_id=data['user_id'],
            template_id=data['template_id'],
            variables=data.get('variables', {})
        )

        return StandardResponse.success({
            'notification_id': notification_id,
            'status': 'queued', # To be an enum later
            'message': 'Email notification queued successfully.'
        }), 200

    except Exception as e:
        return StandardResponse.error('queue_error', str(e)), 500