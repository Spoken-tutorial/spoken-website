# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0014_auto_20180316_1206'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialsAvailable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.ForeignKey(to='creation.Language')),
                ('tutorial_detail', models.ForeignKey(to='creation.TutorialDetail')),
            ],
        ),
        migrations.AddField(
            model_name='tutorialresource',
            name='extension_status',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialsavailable',
            unique_together=set([('tutorial_detail', 'language')]),
        ),
    ]
