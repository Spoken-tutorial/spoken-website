# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_auto_20180411_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancetestbatch',
            name='test',
            field=models.OneToOneField(related_name='advance_test', to='events.AdvanceTest'),
        ),
    ]
