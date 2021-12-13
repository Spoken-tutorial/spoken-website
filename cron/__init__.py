from redis import Redis
# Initialize redis client
REDIS_CLIENT = Redis(
    host='localhost',
    port=6379,
    db=0
)

from rq import Retry, Queue

DEFAULT_QUEUE = Queue('default_queue', connection=REDIS_CLIENT, failure_ttl='72h')
TOPPER_QUEUE = Queue('topper_queue', connection=REDIS_CLIENT, failure_ttl='72h')