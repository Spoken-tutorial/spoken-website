# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0014_auto_20180530_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialresource',
            name='payment_status',
        ),
    ]
