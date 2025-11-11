#!/usr/bin/env python
"""Standardizes response format matching OpenAPI specifications."""
from datetime import datetime
from typing import Any, Optional, Dict


class StandardResponse:
    """Standard response for API endpoints."""

    @staticmethod
    def success(data: Any, message: str, meta: Optional[Dict] = None) -> Dict:
        """Standardise success response format."""
        return {
            "success": True,
            "data": data,
            "message": message,
            "meta": meta
        }

    @staticmethod
    def error(error: str, message: str, meta: Optional[Dict] = None) -> Dict:
        """Standardize the error response format."""
        return {
            "success": False,
            "error": error,
            "message": message,
            "meta": meta
        }

class NotificationResponse:
    """Response Model for notification creation"""

    @staticmethod
    def create(notification_id: str, status: str, estimated_delivery: Optional[str] = None) -> Dict:
        """Create notification response data"""
        data = {
            'notification_id': notification_id,
            'status': status,
        }
        if estimated_delivery:
            data['estimated_delivery'] = estimated_delivery

        return data

    class StatusResponse:
        """Response model for notification status retrieval"""

        @staticmethod
        def create(
                notification_id: str,
                status: str,
                created_at: str,
                updated_at: str,
                delivery_info: Optional[Dict] = None
        ) -> Dict:
            """Create status response data"""
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
        """Response model for health check endpoint"""

        @staticmethod
        def create(
                status: str = 'healthy',
                service: str = 'api-gateway',
                dependencies: Optional[Dict[str, str]] = None
        ) -> Dict:
            """Create health response data"""
            response = {
                'status': status,
                'service': service,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            if dependencies:
                response['dependencies'] = dependencies

            return response
