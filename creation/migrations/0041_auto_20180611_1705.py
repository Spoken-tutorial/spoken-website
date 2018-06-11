# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0040_auto_20180611_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthonorarium',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
