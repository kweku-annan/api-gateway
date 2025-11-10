import redis

# Connect to Redis server
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Set a value
value = r.get('test_key')
print(f'Retrieved from redis: {value}')

# Set with expiration (5 seconds)
r.setex('temp_key', 5, 'I will expire soon')
print('Set temp_key with expiration of 5 seconds.')

