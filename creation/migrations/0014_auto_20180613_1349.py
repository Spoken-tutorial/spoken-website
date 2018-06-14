# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_videotestimonial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videotestimonial',
            old_name='foss_id',
            new_name='foss',
        ),
    ]
