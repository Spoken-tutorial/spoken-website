# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0016_mediatestimonials_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediatestimonials',
            name='foss',
        ),
        migrations.DeleteModel(
            name='MediaTestimonials',
        ),
    ]
