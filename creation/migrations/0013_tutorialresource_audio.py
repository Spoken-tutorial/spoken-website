# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialresource',
            name='audio',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
