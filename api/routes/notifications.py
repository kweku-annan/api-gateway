"""
Notification endpoints
Matches /notifications/* paths in swagger.yaml
"""

from flask import Blueprint, request, jsonify, current_app
import uuid
from datetime import datetime, timedelta

from api.models.response_models import StandardResponse, NotificationResponse, StatusResponse
from api.models.request_models import EmailNotificationRequest, PushNotificationRequest
from api.middleware.auth import require_api_key

# Create blueprint for notification routes
notifications_bp = Blueprint('notifications', __name__)


# NOTE: No more in-memory storage - using RabbitMQ now


@notifications_bp.route('/email', methods=['POST'])
@require_api_key
def send_email_notification():
    """
    Send email notification
    Validates and queues an email notification
    """
    data = request.get_json()

    # Validate request
    validation_errors = EmailNotificationRequest.validate(data, 'email')
    if validation_errors:
        response = StandardResponse.error(
            error='validation_error',
            message='Validation failed: ' + ', '.join(validation_errors)
        )
        return jsonify(response), 400

    # Check if queue service is available
    if not current_app.queue_service or not current_app.queue_service.is_connected():
        response = StandardResponse.error(
            error='service_unavailable',
            message='Notification service is temporarily unavailable'
        )
        return jsonify(response), 503

    try:
        # Publish to queue
        notification_id = current_app.queue_service.publish_notification(
            notification_type='email',
            user_id=data['user_id'],
            template_id=data['template_id'],
            variables=data.get('variables', {}),
            idempotency_key=data.get('idempotency_key')
        )

        # Calculate estimated delivery
        estimated_delivery = (datetime.utcnow() + timedelta(minutes=2)).isoformat() + 'Z'

        # Create response
        response_data = NotificationResponse.create(
            notification_id=notification_id,
            status='queued',
            estimated_delivery=estimated_delivery
        )

        response = StandardResponse.success(
            data=response_data,
            message='Email notification queued successfully'
        )

        return jsonify(response), 202

    except Exception as e:
        current_app.logger.error(f"Failed to queue notification: {str(e)}")
        response = StandardResponse.error(
            error='queue_error',
            message='Failed to queue notification'
        )
        return jsonify(response), 500


@notifications_bp.route('/push', methods=['POST'])
@require_api_key
def send_push_notification():
    """
    Send push notification
    Validates and queues a push notification
    """
    data = request.get_json()

    # Validate request
    validation_errors = PushNotificationRequest.validate(data, 'push')
    if validation_errors:
        response = StandardResponse.error(
            error='validation_error',
            message='Validation failed: ' + ', '.join(validation_errors)
        )
        return jsonify(response), 400

    # Check if queue service is available
    if not current_app.queue_service or not current_app.queue_service.is_connected():
        response = StandardResponse.error(
            error='service_unavailable',
            message='Notification service is temporarily unavailable'
        )
        return jsonify(response), 503

    try:
        # Publish to queue
        notification_id = current_app.queue_service.publish_notification(
            notification_type='push',
            user_id=data['user_id'],
            template_id=data['template_id'],
            variables=data.get('variables', {}),
            idempotency_key=data.get('idempotency_key')
        )

        # Calculate estimated delivery
        estimated_delivery = (datetime.utcnow() + timedelta(minutes=1)).isoformat() + 'Z'

        # Create response
        response_data = NotificationResponse.create(
            notification_id=notification_id,
            status='queued',
            estimated_delivery=estimated_delivery
        )

        response = StandardResponse.success(
            data=response_data,
            message='Push notification queued successfully'
        )

        return jsonify(response), 202

    except Exception as e:
        current_app.logger.error(f"Failed to queue notification: {str(e)}")
        response = StandardResponse.error(
            error='queue_error',
            message='Failed to queue notification'
        )
        return jsonify(response), 500


@notifications_bp.route('/status/<notification_id>', methods=['GET'])
@require_api_key
def get_notification_status(notification_id):
    """
    Get notification status
    Retrieve the status of a previously submitted notification

    """
    response = StandardResponse.error(
        error='not_implemented',
        message='Status tracking will be available after Redis integration'
    )
    return jsonify(response), 501