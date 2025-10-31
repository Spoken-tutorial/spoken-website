# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0036_auto_20180824_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediatestimonials',
            name='workshop_details',
            field=models.CharField(default=b'Workshop', max_length=255),
        ),
        migrations.AlterField(
            model_name='mediatestimonials',
            name='content',
            field=models.CharField(max_length=500),
        ),
    ]
