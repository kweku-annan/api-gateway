#!/usr/bin/env python3
"""Notification request models."""


class NotificationRequest:
    """Notification request model."""
    REQUIRED_FIELDS = ['user_id', 'template_id']
    OPTIONAL_FIELDS = ['variables', 'request_id', 'priority', 'scheduled_time']
    VALID_PROPERTIES = ['high', 'normal', 'low']

    @classmethod
    def from_dict(cls, data):
        """Create NotificationRequest from dictionary."""
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        notification_request = {
            'user_id': data['user_id'],
            'template_id': data['template_id'],
            'variables': data.get('variables', {}),
            'request_id': data.get('request_id'),
            'priority': data.get('priority', 'normal'),
            'scheduled_time': data.get('scheduled_time')
        }

        if notification_request['priority'] not in cls.VALID_PROPERTIES:
            raise ValueError(f"Invalid priority: {notification_request['priority']}. Must be one of {cls.VALID_PROPERTIES}")

        return notification_request