# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0011_auto_20180119_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialresource',
            name='publish_at',
            field=models.DateTimeField(null=True),
        ),
    ]
