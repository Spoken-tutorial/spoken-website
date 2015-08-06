# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20150731_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traininglanguagefeedback',
            name='name',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
