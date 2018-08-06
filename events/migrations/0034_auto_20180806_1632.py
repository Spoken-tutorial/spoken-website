# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_auto_20180724_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccenter',
            name='status',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
