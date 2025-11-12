"""
Enhanced logging with correlation IDs
"""

import logging
import uuid
from flask import request, g, has_request_context
from datetime import datetime


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records
    """

    def filter(self, record):
        """Add correlation_id to log record"""
        if has_request_context():
            # Get or generate correlation ID
            correlation_id = getattr(g, 'correlation_id', None)
            if not correlation_id:
                correlation_id = str(uuid.uuid4())
                g.correlation_id = correlation_id

            record.correlation_id = correlation_id
            record.api_key = getattr(request, 'api_key', 'none')[:8]  # First 8 chars
        else:
            record.correlation_id = 'no-context'
            record.api_key = 'none'

        return True


def setup_logging(app):
    """
    Configure application logging with correlation IDs

    Args:
        app: Flask application instance
    """
    # Create custom formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(correlation_id)s] [%(api_key)s] '
        '%(levelname)s in %(module)s: %(message)s'
    )

    # Configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())

    # Set log level based on debug mode
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO

    # Configure app logger
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Log startup
    app.logger.info(f"API Gateway started - Environment: {app.config.get('ENV', 'unknown')}")

    # Add before_request handler to generate correlation ID
    @app.before_request
    def before_request():
        """Generate correlation ID for each request"""
        if not hasattr(g, 'correlation_id'):
            # Check if client provided correlation ID
            correlation_id = request.headers.get('X-Correlation-ID')
            if not correlation_id:
                correlation_id = str(uuid.uuid4())
            g.correlation_id = correlation_id
            g.request_start_time = datetime.utcnow()

    # Add after_request handler to log request completion
    @app.after_request
    def after_request(response):
        """Log request completion with duration"""
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds() * 1000
            app.logger.info(
                f"{request.method} {request.path} - {response.status_code} - {duration:.2f}ms"
            )

        # Add correlation ID to response headers
        if hasattr(g, 'correlation_id'):
            response.headers['X-Correlation-ID'] = g.correlation_id

        return response