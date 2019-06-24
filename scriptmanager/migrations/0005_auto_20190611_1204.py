# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scriptmanager', '0004_auto_20190611_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptdetails',
            name='script',
            field=models.ForeignKey(blank=True, to='scriptmanager.Scripts', null=True),
        ),
    ]
