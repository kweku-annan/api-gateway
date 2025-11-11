#!/usr/bin/env python3
"""Rate limiting middleware."""
from functools import wraps
from flask import request, current_app
from api.models.response_models import StandardResponse


def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = getattr(request, 'user_id', None)

        if not user_id:
            return f(*args, **kwargs)

        limit = current_app.config['RATE_LIMIT_PER_MINUTE']
        allowed, count = current_app.cache.check_rate_limit(
            user_id=user_id,
            limit=limit
        )

        if not allowed:
            return StandardResponse.error(
                error_code=429,
                error_message=f'Rate limit of {limit} requests per minute exceeded',
                message='Rate Limit Exceeded!'
            )

        return f(*args, **kwargs)
    return decorated