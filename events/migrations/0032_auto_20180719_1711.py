# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_paymentdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='userId',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
