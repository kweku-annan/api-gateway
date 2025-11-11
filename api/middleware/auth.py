"""
Authentication middleware
Implements API Key authentication matching swagger.yaml securitySchemes
"""

from functools import wraps
from flask import request, jsonify, current_app
from api.models.response_models import StandardResponse


def require_api_key(f):
    """
    Decorator to require API key authentication

    Checks for X-API-Key header as specified in swagger.yaml
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')

        # Check if API key is provided
        if not api_key:
            response = StandardResponse.error(
                error='missing_api_key',
                message='API key is required. Please provide X-API-Key header.'
            )
            return jsonify(response), 401

        # Validate API key
        valid_api_keys = current_app.config.get('API_KEYS', [])

        if not valid_api_keys:
            # No API keys configured - log warning and deny access
            current_app.logger.warning('No API keys configured in environment')
            response = StandardResponse.error(
                error='configuration_error',
                message='API authentication is not properly configured'
            )
            return jsonify(response), 500

        if api_key not in valid_api_keys:
            response = StandardResponse.error(
                error='invalid_api_key',
                message='Invalid API key provided'
            )
            return jsonify(response), 401

        # API key is valid - store it in request context for potential logging
        request.api_key = api_key

        # Continue to the actual route
        return f(*args, **kwargs)

    return decorated_function


def optional_api_key(f):
    """
    Decorator for optional API key authentication
    Validates API key if provided, but doesn't require it
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')

        if api_key:
            # Validate API key if provided
            valid_api_keys = current_app.config.get('API_KEYS', [])

            if api_key in valid_api_keys:
                request.authenticated = True
                request.api_key = api_key
            else:
                request.authenticated = False
        else:
            request.authenticated = False

        return f(*args, **kwargs)

    return decorated_function