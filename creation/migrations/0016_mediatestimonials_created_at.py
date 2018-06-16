# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0015_auto_20180615_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediatestimonials',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 15, 14, 16, 43, 907318, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
