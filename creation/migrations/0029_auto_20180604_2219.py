# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0028_auto_20180604_2218'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='duration',
        ),
        migrations.AddField(
            model_name='tutorialpayment',
            name='sec',
            field=models.PositiveIntegerField(default=1, help_text=b'Tutorial duration in seconds'),
            preserve_default=False,
        ),
    ]
