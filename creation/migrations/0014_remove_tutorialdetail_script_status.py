# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_tutorialdetail_script_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorialdetail',
            name='script_status',
        ),
    ]
