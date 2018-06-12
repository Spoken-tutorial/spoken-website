# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_testattendance_student'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentmaster',
            options={'ordering': ['student__user__first_name']},
        ),
        migrations.AlterField(
            model_name='singletraining',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='singletraining',
            name='ttime',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='singletraining',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='singletrainingattendance',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='singletrainingattendance',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
