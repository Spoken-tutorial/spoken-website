# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_mediatestimonials'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mediatestimonials',
            old_name='created_at',
            new_name='created',
        ),
        migrations.AlterField(
            model_name='testimonials',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 15, 14, 46, 42, 85960, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
