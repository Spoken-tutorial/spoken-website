# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0020_auto_20180601_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='tutorial',
        ),
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tutorialresource',
            name='payment_status',
        ),
        migrations.DeleteModel(
            name='TutorialPayment',
        ),
    ]
