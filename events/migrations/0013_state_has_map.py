# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20150908_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='has_map',
            field=models.BooleanField(default=1),
        ),
    ]
