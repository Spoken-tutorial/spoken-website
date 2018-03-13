# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0025_auto_20171023_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inductioninterest',
            name='other_language',
            field=models.CharField(max_length=100),
        ),
    ]
