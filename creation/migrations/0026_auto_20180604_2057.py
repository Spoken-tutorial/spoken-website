# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0025_auto_20180604_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='payment_challan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='creation.PaymentChallan', null=True),
        ),
    ]
