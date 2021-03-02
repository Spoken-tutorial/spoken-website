# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2021-03-01 13:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0018_tutorialduration_created'),
        ('training', '0007_ilwfossmdlcourses'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventTestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mdlemail', models.EmailField(max_length=255, null=True)),
                ('mdlcourse_id', models.PositiveIntegerField(default=0)),
                ('mdlquiz_id', models.PositiveIntegerField(default=0)),
                ('part_status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='training.TrainingEvents')),
                ('fossid', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='creation.FossCategory')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='training.Participant')),
            ],
        ),
    ]
