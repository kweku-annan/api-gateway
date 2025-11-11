#!/usr/bin/env python3
"""JWT authentication middleware."""
from functools import wraps
from flask import request, current_app
from api.models.response_models import StandardResponse
import jwt

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return StandardResponse.error(
                error_code=401,
                error_message="Token is missing!",
                message="Authentication error",
            )

        try:
            decoded = jwt.decode(
                token,
                current_app.config('JWT_SECRET_KEY'),
                algorithms=[current_app.config('JWT_ALGORITHM')]
            )
            request.user_id = decoded.get('user_id')
            request.user_email = decoded.get('email')

        except jwt.ExpiredSignatureError:
            return StandardResponse.error(
                error_code=401,
                error_message='Token has expired!',
                message='Authentication error',
            )
        except jwt.InvalidTokenError:
            return StandardResponse.error(
                error_code=401,
                error_message='Invalid token!',
                message='Authentication error',
            )

        return f(*args, **kwargs)
    return decorated
