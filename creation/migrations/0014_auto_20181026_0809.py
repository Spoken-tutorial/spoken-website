# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_auto_20180910_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialresource',
            name='submissiondate',
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 2, 12, 0)),
        ),
    ]
