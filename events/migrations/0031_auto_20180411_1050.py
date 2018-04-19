# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_auto_20180411_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancetestbatch',
            name='date_time',
            field=models.DateTimeField(null=True),
        ),
    ]
