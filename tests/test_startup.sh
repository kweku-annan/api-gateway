#!/bin/bash
# Test script to verify Docker container startup
set -e  # Exit on error

echo "============================================"
echo "Docker Container Startup Test"
echo "============================================"

# Cleanup function
cleanup() {
  echo ""
  echo "Cleaning up..."
  docker stop test-gateway 2>/dev/null || true
  docker rm test-gateway 2>/dev/null || true
  docker rmi api-gateway-test 2>/dev/null || true
}

# Register cleanup on exit
trap cleanup EXIT

echo ""
echo "Step 1: Building Docker image..."
docker build -f docker/Dockerfile -t api-gateway-test .

echo ""
echo "Step 2: Running Docker container..."
CONTAINER_ID=$(docker run -d --name test-gateway \
  -e FLASK_ENV=production \
  -e API_KEYS=test-key \
  -e RABBITMQ_HOST=localhost \
  -e REDIS_HOST=localhost \
  -p 5000:5000 \
  api-gateway-test)

echo "Container ID: $CONTAINER_ID"

echo ""
echo "Step 3: Waiting for container to start..."
for i in {1..30}; do
  echo -n "."
  sleep 1

  # Check if container is still running
  if ! docker ps | grep -q test-gateway; then
    echo ""
    echo "❌ Container stopped unexpectedly!"
    echo ""
    echo "Container logs:"
    docker logs test-gateway
    exit 1
  fi

  # Try to curl the health endpoint
  if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    echo ""
    echo "✓ Container is responding!"
    break
  fi
done

echo ""
echo "Step 4: Checking container status..."
docker ps | grep test-gateway || echo "Container not running!"

echo ""
echo "Step 5: Checking container logs..."
echo "----------------------------------------"
docker logs test-gateway
echo "----------------------------------------"

echo ""
echo "Step 6: Testing health endpoint..."
echo "----------------------------------------"
RESPONSE=$(curl -f -s http://localhost:5000/health)
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "Step 7: Checking response structure..."
if echo "$RESPONSE" | grep -q '"status":"healthy"'; then
  echo "✓ Health check passed!"
else
  echo "❌ Health check failed - unexpected response"
  exit 1
fi

echo ""
echo "============================================"
echo "✓ All tests passed!"
echo "============================================"

