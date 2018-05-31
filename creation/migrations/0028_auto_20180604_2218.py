# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0027_auto_20180604_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialpayment',
            name='duration',
            field=models.PositiveIntegerField(help_text=b'Tutorial duration in seconds'),
        ),
    ]
