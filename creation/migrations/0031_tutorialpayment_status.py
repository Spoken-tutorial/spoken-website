# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0030_auto_20180604_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialpayment',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, b'Payment Cancelled'), (1, b'Payment Due'), (2, b'Payment Initiated')]),
        ),
    ]
