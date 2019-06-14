# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scriptmanager', '0005_auto_20190611_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptdetails',
            name='script',
            field=models.ForeignKey(default=False, to='scriptmanager.Scripts'),
            preserve_default=False,
        ),
    ]
