class GatewayException(Exception):
    """Base exception for Gateway"""
    pass

class UserServiceError(GatewayException):
    """User Service communication error"""
    pass

class QueueError(GatewayException):
    """RabbitMQ error"""
    pass

class CacheError(GatewayException):
    """Redis cache error"""
    pass

class CircuitOpenError(GatewayException):
    """Circuit breaker is open"""
    pass

class ValidationError(GatewayException):
    """Request validation error"""
    pass