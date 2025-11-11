#!/usr/bin/env python3
"""Notifications endpoints."""

from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, timedelta

from api.models.response_models import StandardResponse, NotificationResponse, StatusResponse
from api.models.request_models import EmailNotificationRequest, PushNotificationRequest
from api.middleware.auth import require_api_key

notifications_bp = Blueprint('notifications', __name__)

# Temporary in-memory storage for demo purposes
# This will be replaced with Redis in later

notification_store = {}

@notifications_bp.route('/email', methods=['POST'])
@require_api_key
def send_email_notification():
    """Send email notification."""
    data = request.get_json()

    # Validate request data
    validation_error = EmailNotificationRequest.validate(data, 'email')
    if validation_error:
        response = StandardResponse.error(
            error='validation_error',
            message='Validation failed: ' + ', '.join(validation_error)
        )
        return jsonify(response), 400

    # Check idempotency (if key provided)
    idempotency_key = data.get('idempotency_key')
    if idempotency_key and idempotency_key in notification_store:
        # Return cached response
        cached = notification_store[idempotency_key]
        response = StandardResponse.success(
            data=cached['response_data'],
            message='Notification already queued (idempotent)'
        )
        return jsonify(response), 202

    # Generate notification ID
    notification_id = str(uuid.uuid4())

    # Calculate estimated delivery (mock: 2 minutes from now)
    estimated_delivery = (datetime.utcnow() + timedelta(minutes=2)).isoformat() + 'Z'

    # Create response data
    response_data = NotificationResponse.create(
        notification_id=notification_id,
        status='queued',
        estimated_delivery=estimated_delivery
    )

    # Store notification status (mock storage)
    notification_store[notification_id] = {
        'notification_id': notification_id,
        'type': 'email',
        'status': 'queued',
        'template_id': data['template_id'],
        'user_id': data['user_id'],
        'variables': data.get('variables', {}),
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'response_data': response_data
    }

    # Store by idempotency key if provided
    if idempotency_key:
        notification_store[idempotency_key] = notification_store[notification_id]

    response = StandardResponse.success(
        data=response_data,
        message='Email notification queued successfully'
    )

    return jsonify(response), 202

@notifications_bp.route('/push', methods=['POST'])
@require_api_key
def send_push_notification():
    """Send push notification."""
    data = request.get_json()

    # Validate request data
    validation_error = PushNotificationRequest.validate(data, 'push')
    if validation_error:
        response = StandardResponse.error(
            error='validation_error',
            message='Validation failed: ' + ', '.join(validation_error)
        )
        return jsonify(response), 400

    # Check idempotency (if key provided)
    idempotency_key = data.get('idempotency_key')
    if idempotency_key and idempotency_key in notification_store:
        # Return cached response
        cached = notification_store[idempotency_key]
        response = StandardResponse.success(
            data=cached['response_data'],
            message='Notification already queued (idempotent)'
        )
        return jsonify(response), 202

    # Generate notification ID
    notification_id = str(uuid.uuid4())

    # Calculate estimated delivery (mock: 1 minute from now)
    estimated_delivery = (datetime.utcnow() + timedelta(minutes=1)).isoformat() + 'Z'

    # Create response data
    response_data = NotificationResponse.create(
        notification_id=notification_id,
        status='queued',
        estimated_delivery=estimated_delivery
    )

    # Store notification status (mock storage)
    notification_store[notification_id] = {
        'notification_id': notification_id,
        'type': 'push',
        'status': 'queued',
        'template_id': data['template_id'],
        'user_id': data['user_id'],
        'variables': data.get('variables', {}),
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'response_data': response_data
    }

    # Store by idempotency key if provided
    if idempotency_key:
        notification_store[idempotency_key] = notification_store[notification_id]

    response = StandardResponse.success(
        data=response_data,
        message='Push notification queued successfully'
    )

    return jsonify(response), 202

@notifications_bp.route('/status/<notification_id>', methods=['GET'])
@require_api_key
def get_notification_status(notification_id):
    """Get notification status."""
    notification = notification_store.get(notification_id)
    if not notification:
        response = StandardResponse.error(
            error='not_found',
            message=f'Notification ID {notification_id} not found'
        )
        return jsonify(response), 404

    response_data = StatusResponse.create(
        notification_id=notification['notification_id'],
        status=notification['status'],
        created_at=notification['created_at'],
        updated_at=notification['updated_at'],
        delivery_info={
            'type': notification['type'],
            'user_id': notification['user_id'],
            'template_id': notification['template_id']
        }
    )

    # Create success response
    response = StandardResponse.success(
        data=response_data,
        message='Notification status retrieved successfully'
    )

    return jsonify(response), 200