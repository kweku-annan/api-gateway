#!/usr/bin/env python3
"""Radis interaction implementation."""
import redis
import json
from flask import current_app
from api.exceptions.custom_exceptions import CacheError


class CacheService:
    """Handles Redis caching operations"""

    def __init__(self):
        config = current_app.config
        self.client = redis.Redis(
            host=config['REDIS_HOST'],
            port=config['REDIS_PORT'],
            db=config['REDIS_DB'],
            # password=config.get('REDIS_PASSWORD', None),
            decode_responses=True
        )

    def get(self, key):
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value) if value.startswith('{') else value
            return None
        except Exception as e:
            current_app.logger.warning(f"Cache get failed: {str(e)}")
            return None

    def set(self, key, value, ttl=3600):
        """Set value in cache with optional TTL"""
        try:
            if isinstance(value, (dict, list))
                value = json.dumps(value)
        except Exception as e:
            current_app.logger.warning(f"Cache set failed: {str(e)}")

    def check_idempotency(self, request_id):
        """Check if request was already processed"""
        key = f"request:{request_id}"
        return self.get(key)

    def store_idempotency(self, request_id, response, ttl=86400):
        """Store idempotent response"""
        key = f"request:{request_id}"
        self.set(key, response, ttl)

    def get_notification_status(self, notification_id):
        """Get notification status from cache"""
        key = f"notification:{notification_id}:status"
        return self.get(key)

    def set_notification_status(self, notification_id, status, ttl=86400):
        """Set notification status in cache"""
        key = f"notification:{notification_id}:status"
        self.set(key, status, ttl)

    def check_rate_limit(self, user_id, limit=100, window=60):
        """Check rate limit for user"""
        key = f"rate_limit:{user_id}"
        try:
            count = self.client.incr(key)
            if count == 1:
                self.client.expire(key, window)
            return count <= limit, count
        except Exception as e:
            current_app.logger.warning(f"Rate limit check failed: {str(e)}")
            return True, 0  # Allow on cache failure

    def check_connection(self):
        """Check if Redis is connected"""
        try:
            self.client.ping()
            return True
        except:
            return False