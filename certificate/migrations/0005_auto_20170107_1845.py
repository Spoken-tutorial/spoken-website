# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0004_auto_20160818_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='purpose',
            field=models.CharField(max_length=25, choices=[(b'DCM', b'DrupalCamp Mumbai'), (b'DRP', b'Drupal Workshop')]),
        ),
    ]
