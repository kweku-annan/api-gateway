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

    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    # Server settings
    PORT = int(os.getenv('PORT', 5000))

    # User Service
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 100))



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