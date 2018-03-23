# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0009_auto_20170612_1543'),
        ('events', '0027_inductionfinallist'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvanceTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('qualifying_marks', models.DecimalField(default=90, max_digits=5, decimal_places=2)),
                ('foss', models.ForeignKey(related_name='advance_test_foss', to='creation.FossCategory')),
            ],
        ),
        migrations.CreateModel(
            name='AdvanceTestBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_open', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(related_name='advance_batch', to='events.StudentBatch', null=True)),
                ('students', models.ManyToManyField(related_name='advance_students', null=True, to='events.Student')),
                ('test', models.ForeignKey(related_name='advance_test', to='events.AdvanceTest')),
            ],
        ),
    ]
