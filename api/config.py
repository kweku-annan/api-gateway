#!/usr/bin/env python3
"""Configuration for API Gateway"""

import os
from dotenv import load_dotenv

# Load environment variable from .env file
load_dotenv()

class Config:
    "Base Configuration"
    # Flask settings

    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # Server settings
    PORT = int(os.getenv('PORT', 5000))

class DevelopmentConfig(Config):
    "Development Configuration"
    DEBUG = True

class ProductionConfig(Config):
    "Production Configuration"
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}