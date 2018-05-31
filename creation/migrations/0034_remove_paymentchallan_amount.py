# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0033_auto_20180605_0002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentchallan',
            name='amount',
        ),
    ]
