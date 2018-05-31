# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0029_auto_20180604_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='sec',
        ),
        migrations.AddField(
            model_name='tutorialpayment',
            name='seconds',
            field=models.PositiveIntegerField(default=0, help_text=b'Tutorial duration in seconds'),
        ),
    ]
