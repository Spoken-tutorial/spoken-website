# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scriptmanager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cue', models.TextField()),
                ('narration', models.TextField()),
                ('order', models.PositiveIntegerField()),
                ('script', models.ForeignKey(to='scriptmanager.Scripts')),
            ],
        ),
    ]
