# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0017_auto_20180601_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialresource',
            name='payment_status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, b'Payment Due'), (1, b'Payment Initiated'), (2, b'Payment Forwarded'), (3, b'Payment Done')]),
        ),
    ]
