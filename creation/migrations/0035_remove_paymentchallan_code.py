# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0034_remove_paymentchallan_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentchallan',
            name='code',
        ),
    ]
