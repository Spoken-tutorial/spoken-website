# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0009_auto_20170612_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialresource',
            name='publish_date',
            field=models.DateTimeField(null=True),
        ),
    ]
