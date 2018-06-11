# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0039_auto_20180606_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
