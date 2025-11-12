#!/usr/bin/env python3
"""Run the Flask application."""

from api.main import create_app
from api.config import Config
import os
import sys

# Print startup info for debugging
print("=" * 60, file=sys.stderr)
print("API Gateway Starting...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}", file=sys.stderr)
print(f"PORT: {os.getenv('PORT', 'not set')}", file=sys.stderr)
print(f"API_KEYS: {'set' if os.getenv('API_KEYS') else 'not set'}", file=sys.stderr)
print(f"RABBITMQ_HOST: {os.getenv('RABBITMQ_HOST', 'not set')}", file=sys.stderr)
print(f"REDIS_HOST: {os.getenv('REDIS_HOST', 'not set')}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Create app instance for gunicorn
# Use FLASK_ENV to determine config, default to production for safety
config_name = os.getenv('FLASK_ENV', 'production')
print(f"Loading config: {config_name}", file=sys.stderr)

try:
    app = create_app(config_name)
    print("✓ App created successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to create app: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    port = Config.PORT
    print(f"Starting development server on 0.0.0.0:{port}", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

