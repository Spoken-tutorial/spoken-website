from redis import Redis
# Initialize redis client
REDIS_CLIENT = Redis(
    host='localhost',
    port=6379,
    db=0
)

from rq import Retry, Queue

DEFAULT_QUEUE = Queue('default', connection=REDIS_CLIENT, timeout='24h', retry=Retry(max=2))