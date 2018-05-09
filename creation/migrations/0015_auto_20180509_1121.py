# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0014_auto_20180502_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributorrole',
            name='tutorial_detail',
            field=models.ForeignKey(to='creation.TutorialDetail', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='contributorrole',
            unique_together=set([('user', 'foss_category', 'language', 'tutorial_detail')]),
        ),
    ]
