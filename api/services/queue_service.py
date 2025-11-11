#!/usr/bin/env python3
"""All RabbitMQ related services."""
import pika
import json
import uuid
from datetime import datetime
from flask import current_app
from api.exceptions.custom_exceptions import QueueError


class MessageQueue:
    """Handles RabbitMQ message publishing"""
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Establish connection to RabbitMQ"""
        config = current_app.config
        credentials = pika.PlainCredentials(
            config['RABBITMQ_USER'],
            config['RABBITMQ_PASSWORD']
        )
        parameters = pika.ConnectionParameters(
            host=config['RABBITMQ_HOST'],
            port=config['RABBITMQ_PORT'],
            credentials=credentials
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self._setup_queues()

    def _setup_queues(self):
        """Declare exchange and queues"""
        # Declare exchange
        self.channel.exchange_declare(
            exchange='notifications.direct',
            exchange_type='direct',
            durable=True
        )

        # Declare queues and bind
        for queue_name, routing_key in [
            ('email.queue', 'email'),
            ('failed.queue', 'failed'),
            ('push.queue', 'push')
        ]:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange='notifications.direct',
                queue=queue_name,
                routing_key=routing_key
            )

    def publish_notification(self, notification_type, user_id, template_id,
                             variables, request_id=None):
        """Publish notification message to RabbitMQ"""
        message = {
            'notification_id': str(uuid.uuid4()),
            'request_id': request_id or str(uuid.uuid4()),
            'correlation_id': str(uuid.uuid4()),
            'type': notification_type,
            'user_id': user_id,
            'template_id': template_id,
            'variables': variables,
            'timestamps': {
                'created_at': datetime.utcnow().isoformat() + 'Z'
            },
            'retry_count': 0,
            'max_retries': 3
        }

        try:
            self.channel.basic_publish(
                exchange='notifications.direct',
                routing_key=notification_type,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                )
            )
            return message['notification_id']
        except Exception as e:
            raise QueueError(f"Failed to publish message: {str(e)}")

    def check_connection(self):
        """Check if RabbitMQ is connected"""
        try:
            return self.connection and self.connection.is_open
        except:
            return False


    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()

