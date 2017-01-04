import logging
from spoken.celery import app

logger = logging.getLogger(__name__)


@app.task(name='test_scheduled_task', ignore_result=True)
def test_scheduled_task():
    logger.info('Celery test task...')

