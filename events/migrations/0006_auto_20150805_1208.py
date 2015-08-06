# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_organiserfeedback'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpfulFor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('helpful_for', models.CharField(max_length=50, choices=[(b'0', b'Academic Performance'), (b'1', b'Project Assignments'), (b'2', b'To get job interviews'), (b'3', b'To get jobs'), (b'4', b'All of the    above')])),
            ],
        ),
        migrations.CreateModel(
            name='StudentStream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student_stream', models.CharField(max_length=50, choices=[(b'0', b'Engineering'), (b'1', b'science'), (b'2', b'Arts and Humanities'), (b'3', b'Polytechnic/ Diploma programs'), (b'4', b'Commerce and Business Studies'), (b'5', b'Schools'), (b'6', b'ITI'), (b'7', b'other (need to give textbox)')])),
            ],
        ),
        migrations.RemoveField(
            model_name='organiserfeedback',
            name='helpful_for',
        ),
        migrations.RemoveField(
            model_name='organiserfeedback',
            name='student_stream',
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='helpful_for',
            field=models.ManyToManyField(related_name='events_HelpfulFor_related', to='events.HelpfulFor'),
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='student_stream',
            field=models.ManyToManyField(related_name='events_StudentStream_related', to='events.StudentStream'),
        ),
    ]
