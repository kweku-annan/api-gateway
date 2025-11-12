#!/usr/bin/env python3
"""Rate limiting middleware using Redis"""
from flask import request, jsonify, current_app
from functools import wraps
from api.models.response_models import StandardResponse


def rate_limit(f):
    """Decorator to apply rate limiting to endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if cache service is available
        if not hasattr(current_app, 'cache_service') or not current_app.cache_service:
            # No cache service - skip rate limiting
            current_app.logger.warning('Cache service not available for rate limiting')
            return f(*args, **kwargs)

        # Use API key as identifier if available, else use IP address
        identifier = getattr(request, 'api_key', None)
        if not identifier:
            # No identifier, skip rate limiting
            current_app.logger.warning('No identifier for rate limiting, skipping')
            return f(*args, **kwargs)

        allowed, current_count = current_app.cache_service.check_rate_limit(identifier)

        if not allowed:
            # Get rate limit info for response
            rate_info = current_app.cache_service.get_rate_limit_info(identifier)

            response = StandardResponse.error(
                error='rate_limit_exceeded',
                message=f"Rate limit exceeded. Limit: {rate_info['limit']} requests per minute. Try again in {rate_info['reset_in_seconds']} seconds.",
                meta={
                    'rate_limit': rate_info
                }
            )
            return jsonify(response), 429

        # Add rate limit info to response headers
        rate_info = current_app.cache_service.get_rate_limit_info(identifier)

        # Continue to endpoint
        response = f(*args, **kwargs)

        # Add rate limit headers if response is a tuple (response, status)
        if isinstance(response, tuple) and len(response) >= 2:
            data, status_code = response[0], response[1]
            return data, status_code, {
                'X-RateLimit-Limit': str(rate_info['limit']),
                'X-RateLimit-Remaining': str(rate_info['remaining']),
                'X-RateLimit-Reset': str(rate_info['reset_in_seconds'])
            }
        return response
    return decorated_function

