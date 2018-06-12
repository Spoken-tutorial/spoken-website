# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20150908_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='verified',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
