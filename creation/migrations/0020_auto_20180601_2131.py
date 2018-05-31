# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0019_auto_20180601_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='time',
            field=models.TextField(default=b''),
        ),
    ]
