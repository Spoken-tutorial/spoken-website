# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20151222_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='has_map',
            field=models.BooleanField(default=1),
        ),
        migrations.AlterField(
            model_name='trainingrequest',
            name='status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
