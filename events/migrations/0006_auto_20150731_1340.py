# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20150731_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traininglanguagefeedback',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest'),
        ),
    ]
