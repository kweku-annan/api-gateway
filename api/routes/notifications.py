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
from api.middleware.rate_limiter import rate_limit

# Create blueprint for notification routes
notifications_bp = Blueprint('notifications', __name__)


# NOTE: No more in-memory storage - using RabbitMQ now


@notifications_bp.route('/email', methods=['POST'])
@require_api_key
@rate_limit
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

    # Check idempotency if key provided and Redis available
    idempotency_key = data.get('idempotency_key')
    if idempotency_key and current_app.cache_service:
        cached_response = current_app.cache_service.check_idempotency(idempotency_key)
        if cached_response:
            current_app.logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
            return jsonify(cached_response), 20

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

        # Store notification status in Redis
        if current_app.cache_service:
            status_data = {
                'notification_id': notification_id,
                'type': 'email',
                'status': 'queued',
                'user_id': data['user_id'],
                'template_id': data['template_id'],
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'updated_at': datetime.utcnow().isoformat() + 'Z'
            }
            current_app.cache_service.set_notification_status(notification_id, status_data)

            # Store for idempotency if key provided
            if idempotency_key:
                current_app.cache_service.store_idempotency(idempotency_key, response)

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
@rate_limit
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

    # Check idempotency
    idempotency_key = data.get('idempotency_key')
    if idempotency_key and current_app.cache_service:
        cached_response = current_app.cache_service.check_idempotency(idempotency_key)
        if cached_response:
            return jsonify(cached_response), 202

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
            idempotency_key=idempotency_key
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

        # Store notification status in Redis
        if current_app.cache_service:
            status_data = {
                'notification_id': notification_id,
                'type': 'push',
                'status': 'queued',
                'user_id': data['user_id'],
                'template_id': data['template_id'],
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'updated_at': datetime.utcnow().isoformat() + 'Z'
            }
            current_app.cache_service.set_notification_status(notification_id, status_data)

            # Store for idempotency
            if idempotency_key:
                current_app.cache_service.store_idempotency(idempotency_key, response)

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
    # Check if cache service is available
    if not current_app.cache_service or not current_app.cache_service.is_connected():
        response = StandardResponse.error(
            error='service_unavailable',
            message='Status service is temporarily unavailable'
        )
        return jsonify(response), 503

    # Get status from Redis
    status_data = current_app.cache_service.get_notification_status(notification_id)

    if not status_data:
        response = StandardResponse.error(
            error='not_found',
            message=f'Notification {notification_id} not found'
        )
        return jsonify(response), 404

    # Create status response
    response_data = StatusResponse.create(
        notification_id=status_data['notification_id'],
        status=status_data['status'],
        created_at=status_data['created_at'],
        updated_at=status_data['updated_at'],
        delivery_info={
            'type': status_data['type'],
            'user_id': status_data['user_id'],
            'template_id': status_data['template_id']
        }
    )

    response = StandardResponse.success(
        data=response_data,
        message='Notification status retrieved successfully'
    )

    return jsonify(response), 200