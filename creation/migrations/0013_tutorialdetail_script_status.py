# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialdetail',
            name='script_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
