# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0022_auto_20171023_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inductioninterest',
            name='do_agree',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='no_objection',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes')]),
        ),
    ]
