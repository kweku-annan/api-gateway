"""
RabbitMQ Queue Service
Handles message queue operations for notification system
"""

import pika
import json
import uuid
from datetime import datetime
from flask import current_app


class QueueService:
    """
    Manages RabbitMQ connections and message publishing
    Implements the queue structure from project requirements
    """

    def __init__(self):
        """Initialize queue service (connection happens lazily)"""
        self.connection = None
        self.channel = None
        self.exchange_name = None

    def connect(self):
        """
        Establish connection to RabbitMQ and setup exchange/queues
        Supports both RABBITMQ_URL and individual config variables
        """
        try:
            config = current_app.config

            # Check if RABBITMQ_URL is provided (CloudAMQP, RabbitMQ Cloud, etc.)
            if config.get('RABBITMQ_URL'):
                # Use URL-based connection (supports amqp://, amqps://, etc.)
                parameters = pika.URLParameters(config['RABBITMQ_URL'])
                # Override heartbeat and timeout for production stability
                parameters.heartbeat = 600
                parameters.blocked_connection_timeout = 300

                current_app.logger.info(f"Connecting to RabbitMQ via URL")
            else:
                # Fallback to individual configuration variables
                credentials = pika.PlainCredentials(
                    config['RABBITMQ_USER'],
                    config['RABBITMQ_PASSWORD']
                )

                parameters = pika.ConnectionParameters(
                    host=config['RABBITMQ_HOST'],
                    port=config['RABBITMQ_PORT'],
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )

                current_app.logger.info(f"Connecting to RabbitMQ at {config['RABBITMQ_HOST']}:{config['RABBITMQ_PORT']}")

            # Establish connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.exchange_name = config['RABBITMQ_EXCHANGE']

            # Setup exchange and queues
            self._setup_exchange_and_queues()

            current_app.logger.info("Successfully connected to RabbitMQ")

        except Exception as e:
            current_app.logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def _setup_exchange_and_queues(self):
        """
        Setup exchange, queues and bindings
        Exchange: notifications.direct (direct type)
        Queues: email.queue, push.queue, failed.queue
        """
        # Declare exchange (direct type as per requirements)
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='direct',
            durable=True
        )

        # Declare queues
        queues = [
            ('email.queue', 'email'),
            ('push.queue', 'push')
            # ('failed.queue', 'failed')
        ]

        for queue_name, routing_key in queues:
            # Declare queue
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                auto_delete=False,
                exclusive=False,
                arguments=None  # Match Go service (nil arguments)
            )

            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )

        current_app.logger.info(f"Exchange and queues setup complete")

    def publish_notification(
            self,
            notification_type,
            user_id,
            template_id=None,
            variables=None,
            idempotency_key=None,
            title=None,
            msg=None,
            player_id=None,
            to_email=None,
            from_email=None,
            subject=None,
            content=None,
            html_content=None,
            metadata=None
    ):
        """
        Publish a notification message to the appropriate queue

        Args:
            notification_type: 'email' or 'push'
            user_id: UUID of the user
            template_id: Template identifier
            variables: Dictionary of template variables
            idempotency_key: Optional idempotency key

        Returns:
            notification_id: UUID of the created notification

        Raises:
            Exception: If publishing fails
        """
        # Ensure connection
        if not self.is_connected():
            self.connect()

        # Generate notification ID
        notification_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        # Build message payload
        message = {
            'notification_id': notification_id,
            'correlation_id': correlation_id,
            'type': notification_type,
            'user_id': user_id,
            'template_id': template_id,
            'variables': variables or {},
            'idempotency_key': idempotency_key,
            'timestamps': {
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'queued_at': datetime.utcnow().isoformat() + 'Z'
            },
            'retry_count': 0,
            'max_retries': 3,
            "title": title,
            "message": msg,
            "player_id": player_id,
            "to_email": to_email,
            "from_email": from_email,
            "subject": subject,
            "content": content,
            "html_content": html_content,
            "metadata": metadata or {}
        }

        try:
            # Publish message to exchange with routing key
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=notification_type,  # 'email' or 'push'
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json',
                    correlation_id=correlation_id,
                    message_id=notification_id
                )
            )

            current_app.logger.info(
                f"Published {notification_type} notification {notification_id} to queue"
            )

            return notification_id

        except Exception as e:
            current_app.logger.error(f"Failed to publish message: {str(e)}")
            raise

    def is_connected(self):
        """
        Check if RabbitMQ connection is active

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            return (
                    self.connection and
                    self.connection.is_open and
                    self.channel and
                    self.channel.is_open
            )
        except:
            return False

    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            current_app.logger.info("RabbitMQ connection closed")
        except Exception as e:
            current_app.logger.error(f"Error closing RabbitMQ connection: {str(e)}")


# Global instance
_queue_service = None


def get_queue_service():
    """
    Get or create the global QueueService instance

    Returns:
        QueueService instance
    """
    global _queue_service

    if _queue_service is None:
        _queue_service = QueueService()
        _queue_service.connect()

    return _queue_service