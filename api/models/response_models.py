#!/usr/bin/env python
"""Standardizes response format"""


class StandardResponse:
    """Standard response for API endpoints."""

    @staticmethod
    def success(data, message="success", meta=None):
        """Standardise success response format."""
        return {
            "success": True,
            "data": data,
            "message": message,
            "meta": meta
        }

    @staticmethod
    def error(error_code, error_message, meta=None):
        """Standardize the error response format."""
        return {
            "success": False,
            "error": error_message,
            "error_code": error_code,
            "message": "Validation failed",
            "meta": meta
        }
