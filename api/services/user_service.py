#!/usr/bin/env python3
"""User interactions implementation"""
import requests
from flask import current_app
from api.middleware.circuit_breaker import CircuitBreaker
from api.exceptions.custom_exceptions import UserServiceError

class UserService:
    """Handles communication with User Service"""

    def __init__(self):
        self.base_url = current_app.config['USER_SERVICE_URL']
        self.circuit_breaker = CircuitBreaker('user_service')

    def get_user_email(self, user_id):
        """Get user email with caching and circuit breaker"""
        # Check cache first
        cache_key = f"user:{user_id}:email"
        cached = current_app.cache.get(cache_key)
        if cached:
            return cached

        # Call User Service with circuit breaker
        try:
            response = self.circuit_breaker.call(
                requests.get,
                f"{self.base_url}/users/{user_id}",
                timeout=2
            )

            if response.status_code == 200:
                email = response.json().get('email')
                # Cache for 1 hour
                current_app.cache.set(cache_key, email, ttl=3600)
                return email
            else:
                raise UserServiceError(f"User service returned {response.status_code}")

        except Exception as e:
            # Try stale cache as fallback
            stale = current_app.cache.get(cache_key, allow_stale=True)
            if stale:
                return stale
            raise UserServiceError(f"Failed to get user email: {str(e)}")

    def get_user_preferences(self, user_id, preferences):
        """Get user preferences from User Service"""
        pass
