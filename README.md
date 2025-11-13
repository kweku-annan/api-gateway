# API Gateway Service

Entry point for the distributed notification system. Handles authentication, validation, rate limiting, and routes messages to appropriate queues.

## Features

- ✅ RESTful API for email and push notifications
- ✅ API Key authentication
- ✅ Request validation
- ✅ Rate limiting (100 req/min per API key)
- ✅ Idempotency support
- ✅ RabbitMQ message queuing
- ✅ Redis caching and status tracking
- ✅ Health check endpoint
- ✅ Correlation ID tracking
- ✅ Docker support
- ✅ CI/CD pipeline

## Architecture
```
Client → API Gateway → RabbitMQ → [Email Service | Push Service]
                    ↓
                  Redis (cache, rate limiting, status)
```

## Microservices

This API Gateway is part of a distributed notification system consisting of the following microservices:

### Service Repositories

1. **API Gateway** (This Repository)
   - Repository: [https://github.com/kweku-annan/api-gateway](https://github.com/kweku-annan/api-gateway)
   - Description: Entry point for the notification system. Handles authentication, validation, rate limiting, and message routing.

2. **Email Service**
   - Repository: [https://github.com/rillexhacks/hng-stage4-email-service](https://github.com/rillexhacks/hng-stage4-email-service)
   - Description: Processes email notifications from the queue and sends emails via SMTP or email providers.

3. **Push Notifications Service**
   - Repository: [https://github.com/whotterre/push_notifications](https://github.com/whotterre/push_notifications)
   - Description: Handles push notifications for mobile and web applications.

4. **User Service**
   - Repository: [https://github.com/Gentwocoder/HNG-STAGE4](https://github.com/Gentwocoder/HNG-STAGE4)
   - Description: Manages user data, preferences, and notification settings.

### Service Communication

All services communicate asynchronously via **RabbitMQ** message queues:
- API Gateway publishes messages to queues
- Worker services (Email, Push) consume messages from their respective queues
- User Service provides user data and preferences
- Redis is used for caching, rate limiting, and status tracking across services

## API Endpoints

### Health Check
```http
GET /health
```

### Send Email Notification
```http
POST /notifications/email
Headers: X-API-Key: your-api-key
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "template_id": "welcome_email",
  "variables": {
    "name": "John Doe",
    "order_id": "12345"
  },
  "idempotency_key": "optional-unique-key"
}
```

### Send Push Notification
```http
POST /notifications/push
Headers: X-API-Key: your-api-key
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "template_id": "order_update",
  "variables": {
    "title": "Order Shipped",
    "message": "Your order has been shipped"
  }
}
```

### Check Notification Status
```http
GET /notifications/status/{notification_id}
Headers: X-API-Key: your-api-key
```

## Setup

### Prerequisites
- Python 3.11+
- RabbitMQ
- Redis
- Docker (optional)

### Local Development

1. **Clone and setup**
```bash
git clone <repository-url>
cd api-gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start dependencies**
```bash
# Start RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

4. **Run application**
```bash
python run.py
```

Application will be available at `http://localhost:5000`

### Railway Deployment (Production)

Deploy to Railway.app with one click:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

**Quick Setup:**
1. Click "Deploy on Railway" or push to GitHub
2. Add environment variables (API_KEYS, RABBITMQ_URL, REDIS_URL)
3. Railway auto-detects Flask and uses gunicorn

**📖 Detailed Guide:** See [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) for complete deployment instructions, troubleshooting, and best practices.

**Required Files:**
- ✅ `Procfile` - Defines start command
- ✅ `railway.json` - Railway configuration
- ✅ `nixpacks.toml` - Build configuration
- ✅ `runtime.txt` - Python version

### Docker Deployment

1. **Using docker-compose (recommended)**
```bash
cd docker
docker-compose up -d
```

This starts:
- API Gateway on port 5000
- RabbitMQ on ports 5672 (AMQP) and 15672 (Management UI)
- Redis on port 6379

2. **Build and run manually**
```bash
# Build image
docker build -f docker/Dockerfile -t api-gateway:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e API_KEYS=your-api-key \
  -e RABBITMQ_HOST=rabbitmq \
  -e REDIS_HOST=redis \
  --name api-gateway \
  api-gateway:latest
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `PORT` | Server port | `5000` |
| `DEBUG` | Debug mode | `True` |
| `API_KEYS` | Comma-separated API keys | - |
| `RABBITMQ_HOST` | RabbitMQ hostname | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `guest` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per API key | `100` |

## Project Structure
```
api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application factory
│   ├── config.py            # Configuration
│   ├── middleware/          # Auth, rate limiting
│   ├── models/              # Request/response models
│   ├── routes/              # API endpoints
│   ├── services/            # RabbitMQ, Redis services
│   └── utils/               # Logging, validation
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/workflows/       # CI/CD
├── .env                     # Environment variables (not in git)
├── .env.example            # Environment template
├── requirements.txt         # Python dependencies
└── run.py                  # Entry point
```

## Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test notification (with API key)
curl -X POST http://localhost:5000/notifications/email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-123" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "template_id": "welcome_email",
    "variables": {"name": "Test User"}
  }'
```

### RabbitMQ Management UI
- URL: http://localhost:15672
- Username: `guest`
- Password: `guest`

Check queues to verify messages are being published.

## Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

Returns status of:
- API Gateway
- RabbitMQ connection
- Redis connection

### Logs

Application logs include:
- Correlation IDs for request tracing
- Request/response times
- API key usage (masked)
- Error details
```bash
# View logs (Docker)
docker logs -f api-gateway

# View logs (local)
# Logs print to console
```

### Correlation IDs

Every request gets a correlation ID for distributed tracing:
- Auto-generated if not provided
- Can be provided via `X-Correlation-ID` header
- Returned in response headers
- Included in all logs

## Rate Limiting

- 100 requests per minute per API key (configurable)
- Returns 429 status when exceeded
- Response includes retry information
- Headers show remaining quota

## Idempotency

Prevent duplicate notifications:
```json
{
  "idempotency_key": "unique-key-12345",
  ...
}
```

Same `idempotency_key` returns cached response (24 hour TTL).

## Error Handling

Standard error response format:
```json
{
  "success": false,
  "error": "error_code",
  "message": "Human readable message",
  "meta": null
}
```

Common error codes:
- `missing_api_key` (401)
- `invalid_api_key` (401)
- `validation_error` (400)
- `rate_limit_exceeded` (429)
- `not_found` (404)
- `service_unavailable` (503)

## Contributing

1. Create feature branch
2. Make changes
3. Run linting: `flake8 app`
4. Test changes
5. Submit pull request

## License

MIT License. See `LICENSE` file for details.

## Support

For support, contact: kwekuannan.dev@gmail.com