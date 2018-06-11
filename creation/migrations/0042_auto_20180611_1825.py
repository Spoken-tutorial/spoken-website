# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0041_auto_20180611_1705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='payment_honorarium',
        ),
        migrations.DeleteModel(
            name='PaymentHonorarium',
        ),
    ]
