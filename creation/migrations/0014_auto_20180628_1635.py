# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_auto_20180615_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='amount',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
        ),
    ]
