#!/usr/bin/env python3
"""Configuration settings for the API application."""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # Server settings
    PORT = int(os.getenv('PORT', 5000))

    # API Key Authentication
    API_KEYS = os.getenv('API_KEYS', '').split(',')
    # Remove empty strings and whitespace
    API_KEYS = [key.strip() for key in API_KEYS if key.strip()]

    #RabbitMQ settings
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'notifications.direct')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}