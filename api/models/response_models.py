#!/usr/bin/env python3
"""
Standard response models matching OpenAPI specification
"""

from datetime import datetime
from typing import Any, Optional, Dict


class StandardResponse:
    """
    Standard API response format
    Matches the response structure in swagger.yaml
    """

    @staticmethod
    def success(data: Any, message: str = "Success", meta: Optional[Dict] = None) -> Dict:
        """
        Create a success response

        Args:
            data: Response data
            message: Success message
            meta: Optional metadata (pagination, etc.)

        Returns:
            Standardized success response dictionary
        """
        return {
            'success': True,
            'data': data,
            'message': message,
            'meta': meta
        }

    @staticmethod
    def error(error: str, message: str, meta: Optional[Dict] = None) -> Dict:
        """
        Create an error response

        Args:
            error: Error code/type
            message: Error message
            meta: Optional metadata

        Returns:
            Standardized error response dictionary
        """
        return {
            'success': False,
            'error': error,
            'message': message,
            'meta': meta
        }


class NotificationResponse:
    """
    Response model for notification creation
    Matches NotificationResponse schema in swagger.yaml
    """

    @staticmethod
    def create(notification_id: str, status: str, estimated_delivery: Optional[str] = None) -> Dict:
        """
        Create notification response data

        Args:
            notification_id: UUID of the notification
            status: Current status (queued, processing, sent, failed)
            estimated_delivery: ISO 8601 timestamp for estimated delivery

        Returns:
            Notification response data
        """
        data = {
            'notification_id': notification_id,
            'status': status
        }

        if estimated_delivery:
            data['estimated_delivery'] = estimated_delivery

        return data


class StatusResponse:
    """
    Response model for notification status
    Matches StatusResponse schema in swagger.yaml
    """

    @staticmethod
    def create(
            notification_id: str,
            status: str,
            created_at: str,
            updated_at: str,
            delivery_info: Optional[Dict] = None
    ) -> Dict:
        """
        Create status response data

        Args:
            notification_id: UUID of the notification
            status: Current status (queued, processing, sent, failed, delivered)
            created_at: ISO 8601 timestamp of creation
            updated_at: ISO 8601 timestamp of last update
            delivery_info: Optional delivery information

        Returns:
            Status response data
        """
        data = {
            'notification_id': notification_id,
            'status': status,
            'created_at': created_at,
            'updated_at': updated_at
        }

        if delivery_info:
            data['delivery_info'] = delivery_info

        return data


class HealthResponse:
    """
    Response model for health check
    Matches HealthResponse schema in swagger.yaml
    """

    @staticmethod
    def create(
            status: str = 'healthy',
            service: str = 'api-gateway',
            dependencies: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Create health check response

        Args:
            status: Service status (healthy/unhealthy)
            service: Service name
            dependencies: Status of dependent services

        Returns:
            Health check response data
        """
        response = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'service': service
        }

        if dependencies:
            response['dependencies'] = dependencies

        return response