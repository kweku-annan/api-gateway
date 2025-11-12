"""
Redis Cache Service
Handles caching, idempotency, status storage, and rate limiting
"""

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
    - General caching
    """

    def __init__(self):
        """Initialize cache service (connection happens lazily)"""
        self.client = None

    def connect(self):
        """Establish connection to Redis"""
        try:
            config = current_app.config

            # Create Redis connection
            self.client = redis.Redis(
                host=config['REDIS_HOST'],
                port=config['REDIS_PORT'],
                db=config['REDIS_DB'],
                password=config['REDIS_PASSWORD'] if config['REDIS_PASSWORD'] else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # Test connection
            self.client.ping()

            current_app.logger.info(
                f"Connected to Redis at {config['REDIS_HOST']}:{config['REDIS_PORT']}"
            )

        except Exception as e:
            current_app.logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def is_connected(self) -> bool:
        """
        Check if Redis connection is active

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if self.client:
                self.client.ping()
                return True
            return False
        except:
            return False

    # ==================== IDEMPOTENCY ====================

    def check_idempotency(self, idempotency_key: str) -> Optional[Dict]:
        """
        Check if request with idempotency key was already processed

        Args:
            idempotency_key: Unique key for the request

        Returns:
            Cached response if found, None otherwise
        """
        try:
            key = f"idempotency:{idempotency_key}"
            cached = self.client.get(key)

            if cached:
                return json.loads(cached)
            return None

        except Exception as e:
            current_app.logger.warning(f"Idempotency check failed: {str(e)}")
            return None

    def store_idempotency(
            self,
            idempotency_key: str,
            response_data: Dict,
            ttl: int = 86400
    ) -> bool:
        """
        Store response for idempotency checking

        Args:
            idempotency_key: Unique key for the request
            response_data: Response to cache
            ttl: Time to live in seconds (default 24 hours)

        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            key = f"idempotency:{idempotency_key}"
            self.client.setex(
                key,
                ttl,
                json.dumps(response_data)
            )
            return True

        except Exception as e:
            current_app.logger.warning(f"Failed to store idempotency: {str(e)}")
            return False

    # ==================== NOTIFICATION STATUS ====================

    def get_notification_status(self, notification_id: str) -> Optional[Dict]:
        """
        Get notification status

        Args:
            notification_id: UUID of the notification

        Returns:
            Status data if found, None otherwise
        """
        try:
            key = f"notification:{notification_id}:status"
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
        """
        Store notification status

        Args:
            notification_id: UUID of the notification
            status_data: Status information
            ttl: Time to live in seconds (default 24 hours)

        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            key = f"notification:{notification_id}:status"
            self.client.setex(
                key,
                ttl,
                json.dumps(status_data)
            )
            return True

        except Exception as e:
            current_app.logger.warning(f"Failed to store notification status: {str(e)}")
            return False

    # ==================== RATE LIMITING ====================

    def check_rate_limit(
            self,
            identifier: str,
            limit: Optional[int] = None,
            window: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded

        Args:
            identifier: Unique identifier (user_id, api_key, etc.)
            limit: Maximum requests allowed (uses config default if None)
            window: Time window in seconds (default 60 seconds)

        Returns:
            Tuple of (allowed: bool, current_count: int)
        """
        try:
            if limit is None:
                limit = current_app.config['RATE_LIMIT_PER_MINUTE']

            key = f"rate_limit:{identifier}"

            # Increment counter
            current_count = self.client.incr(key)

            # Set expiry on first request
            if current_count == 1:
                self.client.expire(key, window)

            # Check if limit exceeded
            allowed = current_count <= limit

            return allowed, current_count

        except Exception as e:
            current_app.logger.warning(f"Rate limit check failed: {str(e)}")
            # Allow request on cache failure (fail open)
            return True, 0

    def get_rate_limit_info(self, identifier: str) -> Dict[str, Any]:
        """
        Get detailed rate limit information

        Args:
            identifier: Unique identifier

        Returns:
            Dictionary with rate limit details
        """
        try:
            key = f"rate_limit:{identifier}"
            count = self.client.get(key)
            ttl = self.client.ttl(key)

            limit = current_app.config['RATE_LIMIT_PER_MINUTE']

            return {
                'limit': limit,
                'remaining': max(0, limit - int(count or 0)),
                'reset_in_seconds': ttl if ttl > 0 else 60
            }

        except Exception as e:
            current_app.logger.warning(f"Failed to get rate limit info: {str(e)}")
            return {
                'limit': 0,
                'remaining': 0,
                'reset_in_seconds': 60
            }

    # ==================== GENERAL CACHING ====================

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            value = self.client.get(key)
            if value:
                # Try to parse as JSON, return as string if fails
                try:
                    return json.loads(value)
                except:
                    return value
            return None

        except Exception as e:
            current_app.logger.warning(f"Cache get failed for key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiry)

        Returns:
            bool: True if successful, False otherwise
        """
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

        Args:
            key: Cache key

        Returns:
            bool: True if deleted, False otherwise
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


# Global instance
_cache_service = None


def get_cache_service():
    """
    Get or create the global CacheService instance

    Returns:
        CacheService instance
    """
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService()
        _cache_service.connect()

    return _cache_service