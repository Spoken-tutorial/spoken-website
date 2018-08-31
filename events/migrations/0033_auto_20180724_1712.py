# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_paymenttransactiondetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='amount',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='paymenttransactiondetails',
            name='amount',
            field=models.CharField(max_length=20),
        ),
    ]
