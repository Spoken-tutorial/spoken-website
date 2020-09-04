from redis import Redis
# Initialize redis client
REDIS_CLIENT = Redis(
    host='localhost',
    port=6379,
    db=0
)