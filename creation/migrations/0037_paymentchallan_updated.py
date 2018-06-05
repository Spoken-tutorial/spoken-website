# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0036_paymentchallan_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentchallan',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 5, 11, 49, 57, 398229, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
