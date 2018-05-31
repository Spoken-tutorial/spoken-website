# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0024_auto_20180604_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='payment_challan',
            field=models.ForeignKey(default=1, to='creation.PaymentChallan'),
            preserve_default=False,
        ),
    ]
