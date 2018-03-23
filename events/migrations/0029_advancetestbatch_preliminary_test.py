# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_advancetest_advancetestbatch'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancetestbatch',
            name='preliminary_test',
            field=models.ForeignKey(related_name='pretest', default=None, to='events.Test'),
            preserve_default=False,
        ),
    ]
