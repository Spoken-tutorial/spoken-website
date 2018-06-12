# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_drupal2018_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='MumbaiStudents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bid', models.ForeignKey(to='events.StudentBatch')),
                ('stuid', models.ForeignKey(to='events.Student')),
            ],
        ),
    ]
