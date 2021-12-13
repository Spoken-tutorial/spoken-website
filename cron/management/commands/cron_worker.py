#!/usr/bin/env python
import sys
from rq import Connection, Worker
from django.core.management.base import BaseCommand, CommandError
# Preload libraries
from cron import DEFAULT_QUEUE, REDIS_CLIENT,TOPPER_QUEUE

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
from rq.job import Job
from rq.command import send_shutdown_command, send_kill_horse_command
from cron.models import AsyncCronMail
from rq.registry import FailedJobRegistry

class Command(BaseCommand):
    def handle(self, *args, **options):
        with Connection(REDIS_CLIENT):
            workers = Worker.all(REDIS_CLIENT)
            for worker in workers:
                send_kill_horse_command(REDIS_CLIENT, worker.name)
                send_shutdown_command(REDIS_CLIENT, worker.name)
                worker.register_death()
            job_ids = AsyncCronMail.objects.values_list('job_id').filter(started_at__isnull=False,status=False).first()
            if AsyncCronMail.objects.filter(started_at__isnull=False,status=False).count() > 0:
                try:
                    job = Job.fetch(job_ids[0], connection=REDIS_CLIENT)
                    DEFAULT_QUEUE.empty()
                    DEFAULT_QUEUE.enqueue_job(job)
                except:
                    print('Job does not exist')
            topper_registry = FailedJobRegistry(queue=TOPPER_QUEUE)
            for job_id in topper_registry.get_job_ids():
                topper_registry.remove(job_id, delete_job=True)
            w = Worker([DEFAULT_QUEUE,TOPPER_QUEUE], connection=REDIS_CLIENT, name='default_worker')
            w.work()

