#!/usr/bin/env python3
"""Run the Flask application."""

from api.main import create_app
from api.config import Config
import os

# Create app instance for gunicorn
# Use FLASK_ENV to determine config, default to production for safety
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    port = Config.PORT
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

