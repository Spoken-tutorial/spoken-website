# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaksh', '0014_auto_20180620_1004'),
        ('events', '0035_auto_20180420_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancetest',
            name='yaksh_course',
            field=models.OneToOneField(default=None, to='yaksh.Course'),
            preserve_default=False,
        ),
    ]
