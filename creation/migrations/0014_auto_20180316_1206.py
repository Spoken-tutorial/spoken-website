# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0013_auto_20180313_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialresource',
            name='assignment_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tutorialresource',
            name='submissiondate',
            field=models.DateTimeField(default=b'2000-01-02', blank=True),
        ),  
        migrations.AlterUniqueTogether(
            name='tutorialresource',
            unique_together=set([('tutorial_detail', 'assignment_status', 'language')]),
        ),
    ]
