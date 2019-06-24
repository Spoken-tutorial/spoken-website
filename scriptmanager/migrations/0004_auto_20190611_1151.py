# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scriptmanager', '0003_auto_20190608_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptdetails',
            name='script',
            field=models.ForeignKey(to='scriptmanager.Scripts', blank=True),
        ),
    ]
