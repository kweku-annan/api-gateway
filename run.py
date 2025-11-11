#!/usr/bin/env python3
"""Run the Flask application."""

from api.main import create_app
from api.config import Config
import os

if __name__ == '__main__':
    app = create_app()
    port = Config.PORT
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

