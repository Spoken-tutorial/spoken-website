# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_auto_20180420_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancetestbatch',
            name='test',
            field=models.ForeignKey(related_name='advance_test', to='events.AdvanceTest'),
        ),
    ]
