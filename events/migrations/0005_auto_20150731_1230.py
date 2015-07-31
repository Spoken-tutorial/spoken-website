# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20150727_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingfeedback',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest'),
        ),
    ]
