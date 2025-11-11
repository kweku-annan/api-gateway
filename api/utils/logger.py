import logging
from flask import request


def setup_logger(app):
    """Configure application logging"""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def log_request():
        """Log incoming requests"""
        app.logger.info(f"{request.method} {request.path}")