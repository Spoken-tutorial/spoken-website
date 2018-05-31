# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0022_auto_20180604_1844'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutorialpayment',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='payment_challan',
        ),
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='tutorial_resource',
        ),
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='user',
        ),
        migrations.DeleteModel(
            name='PaymentChallan',
        ),
        migrations.DeleteModel(
            name='TutorialPayment',
        ),
    ]
