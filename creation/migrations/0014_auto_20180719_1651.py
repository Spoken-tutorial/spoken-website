# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_paymentdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentdetails',
            name='userId',
        ),
        migrations.DeleteModel(
            name='PaymentDetails',
        ),
    ]
