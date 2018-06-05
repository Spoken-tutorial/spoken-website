# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0037_paymentchallan_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentchallan',
            name='amount',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='tutorialpayment',
            name='payment_challan',
            field=models.ForeignKey(related_name='tutorials', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='creation.PaymentChallan', null=True),
        ),
    ]
