#!/usr/bin/env python
import sys
from rq import Connection, Worker
from django.core.management.base import BaseCommand, CommandError
# Preload libraries
from cron import DEFAULT_QUEUE, REDIS_CLIENT

# Provide queue names to listen to as arguments to this script,
# similar to rq worker

class Command(BaseCommand):
    def handle(self, *args, **options):
        with Connection(REDIS_CLIENT):
            w = Worker([DEFAULT_QUEUE], connection=REDIS_CLIENT, name='default_worker')
            w.work()

