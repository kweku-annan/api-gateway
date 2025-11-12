#!/usr/bin/env python3
"""Redis Cache Service"""

import redis
import json
from flask import current_app
from typing import Optional, Dict, Any, Tuple


class CacheService:
    """
    Manages Redis operations for the API Gateway
    - Idempotency tracking
    - Notification status storage
    - Rate limiting
    - General Caching
    """

    def __init__(self):
        """Initialize Cache service (connection happens lazily)"""
        self.client = None

    def connect(self):
        """Establish connection to Redis"""
        try:
            config = current_app.config

            self.client = redis.Redis(
                host=config['REDIS_HOST'],
                port=config['REDIS_PORT'],
                db=config.get('REDIS_DB', 0),
                password=config.get('REDIS_PASSWORD', None),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # Test connection
            self.client.ping()
            current_app.logger.info(f"Connected to Redis at {config['REDIS_HOST']}:{config['REDIS_PORT']}")

        except Exception as e:
            current_app.logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        try:
            return self.client.ping()
        except:
            return False


    # IDEMPOTENCY METHODS
    def check_idempotency(self, idempotency_key: str) -> Optional[Dict]:
        """Check if an idempotency key exists and return associated data"""
        try:
            key = f"idempotency:{idempotency_key}"
            cached = self.client.get(key)

            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            current_app.logger.error(f"Failed to check idempotency key: {str(e)}")
            return None

    def store_idempotency(
            self,
            idempotency_key: str,
            response_data: Dict,
            ttl: int = 86400
    ) -> bool:
        """Store response for idempotency checking"""
        try:
            key = f"idempotency:{idempotency_key}"
            self.client.setex(key, ttl, json.dumps(response_data))
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to store idempotency key: {str(e)}")
            return False


    # NOTIFICATION STATUS METHODS
    def get_notification_status(self, notification_id: str) -> Optional[Dict]:
        """Get notification status by ID"""
        try:
            key = f"notification:{notification_id}: status"
            status = self.client.get(key)

            if status:
                return json.loads(status)
            return None
        except Exception as e:
            current_app.logger.warning(f"Failed to get notification status: {str(e)}")
            return None

    def set_notification_status(
            self,
            notification_id: str,
            status_data: Dict,
            ttl: int = 86400
    ) -> bool:
        """Set notification status by ID"""
        try:
            key = f"notification:{notification_id}:status"
            self.client.setex(key, ttl, json.dumps(status_data))
            return True
        except Exception as e:
            current_app.logger.warning(f"Failed to set notification status: {str(e)}")
            return False

    # GENERAL CACHING METHODS
    def get(self, key: str) -> Optional[Any]:
        """Get value from cached"""
        try:
            value = self.client.get(key)
            if value:
                # Try to parse JSON, fallback to raw string
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            current_app.logger.warning(f"Failed to get cache key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            # Convert dict/list to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)

            return True
        except Exception as e:
            current_app.logger.warning(f"Cache set failed for key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        """
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            current_app.logger.warning(f"Cache delete failed for key {key}: {str(e)}")
            return False

    def close(self):
        """Close Redis connection"""
        try:
            if self.client:
                self.client.close()
                current_app.logger.info("Redis connection closed")
        except Exception as e:
            current_app.logger.error(f"Error closing Redis connection: {str(e)}")

# Global singleton instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get or create the global CacheService instance"""
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService()
        _cache_service.connect()

    return _cache_service


