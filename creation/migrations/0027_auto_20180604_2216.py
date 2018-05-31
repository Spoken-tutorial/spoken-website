# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0026_auto_20180604_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='duration',
            field=models.PositiveIntegerField(default=0, help_text=b'Tutorial duration in seconds'),
        ),
    ]
