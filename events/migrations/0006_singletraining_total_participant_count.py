# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20150821_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='singletraining',
            name='total_participant_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
