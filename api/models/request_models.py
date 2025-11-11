#!/usr/bin/env python3
"""Request validation models matching OpenAPI specification."""
from typing import Dict, List, Optional, Any


class NotificationRequest:
    """Notification request model."""
    REQUIRED_FIELDS = ['user_id', 'template_id']
    OPTIONAL_FIELDS = ['variables', 'idempotency_key']
    VALID_STATUSES = ['queued', 'processing', 'sent', 'failed', 'delivered']

    @staticmethod
    def validate(data: Dict[str, Any], notification_type: str) -> Optional[List[str]]:
        """Validate notification request data."""
        errors = []

        if not data:
            return ['Request body is required']

        for field in NotificationRequest.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                errors.append(f"'{field}' is required.")

        if 'user_id' in data and not isinstance(data['user_id'], str):
            errors.append('user_id must be a string')

        if 'template_id' in data and not isinstance(data['template_id'], str):
            errors.append('template_id must be a string')

        if 'variables' in data:
            if not isinstance(data['variables'], dict):
                errors.append('variables must be an object')
            else:
                # Validate that all variable values are strings (as per swagger)
                for key, value in data['variables'].items():
                    if not isinstance(value, str):
                        errors.append(f'variables.{key} must be a string')

        if 'idempotency_key' in data and not isinstance(data['idempotency_key'], str):
            errors.append('idempotency_key must be a string')

        return errors if errors else None


class EmailNotificationRequest(NotificationRequest):
    """
    Email notification request validation
    Matches EmailNotificationRequest schema in swagger.yaml
    """
    pass


class PushNotificationRequest(NotificationRequest):
    """
    Push notification request validation
    Matches PushNotificationRequest schema in swagger.yaml
    """
    pass
