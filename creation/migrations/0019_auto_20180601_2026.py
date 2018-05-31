# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0018_auto_20180601_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='time',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tutorialresource',
            name='payment_status',
            field=models.PositiveSmallIntegerField(default=4, choices=[(0, b'Payment Due'), (1, b'Payment Initiated'), (2, b'Payment Forwarded'), (3, b'Payment Done')]),
        ),
    ]
