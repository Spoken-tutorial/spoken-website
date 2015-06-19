# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '__first__'),
        ('events', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test', models.BooleanField(default=False)),
                ('category', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('foss',),
            },
        ),
        migrations.CreateModel(
            name='LabCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('even', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SingleTraining',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('training_type', models.PositiveIntegerField(default=0)),
                ('tdate', models.DateField()),
                ('ttime', models.TimeField()),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('participant_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('academic', models.ForeignKey(to='events.AcademicCenter')),
                ('course', models.ForeignKey(to='events2.CourseMap')),
                ('language', models.ForeignKey(to='creation.Language')),
                ('organiser', models.ForeignKey(to='events.Organiser')),
            ],
        ),
        migrations.CreateModel(
            name='SingleTrainingAttendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=100, null=True)),
                ('lastname', models.CharField(max_length=100, null=True)),
                ('gender', models.CharField(max_length=10, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('password', models.CharField(max_length=100, null=True)),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('training', models.ForeignKey(to='events2.SingleTraining')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(max_length=15)),
                ('verified', models.BooleanField(default=False)),
                ('error', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.PositiveIntegerField()),
                ('stcount', models.PositiveIntegerField(default=0)),
                ('academic', models.ForeignKey(to='events.AcademicCenter')),
                ('department', models.ForeignKey(to='events.Department')),
                ('organiser', models.ForeignKey(to='events.Organiser')),
            ],
        ),
        migrations.CreateModel(
            name='StudentMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('moved', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(to='events2.StudentBatch')),
                ('student', models.ForeignKey(to='events2.Student')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingAttend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(default=None, to='creation.Language')),
                ('student', models.ForeignKey(to='events2.Student')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingCertificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=255, null=True)),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('updated', models.DateTimeField()),
                ('student', models.ForeignKey(to='events2.Student')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingPlanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('academic', models.ForeignKey(to='events.AcademicCenter')),
                ('organiser', models.ForeignKey(to='events.Organiser')),
                ('semester', models.ForeignKey(to='events2.Semester')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sem_start_date', models.DateField()),
                ('participants', models.PositiveIntegerField(default=0)),
                ('status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(to='events2.StudentBatch', null=True)),
                ('course', models.ForeignKey(to='events2.CourseMap')),
                ('department', models.ForeignKey(to='events.Department')),
                ('training_planner', models.ForeignKey(to='events2.TrainingPlanner')),
            ],
        ),
        migrations.AddField(
            model_name='trainingcertificate',
            name='training',
            field=models.ForeignKey(to='events2.TrainingRequest'),
        ),
        migrations.AddField(
            model_name='trainingattend',
            name='training',
            field=models.ForeignKey(to='events2.TrainingRequest'),
        ),
        migrations.AddField(
            model_name='coursemap',
            name='course',
            field=models.ForeignKey(blank=True, to='events2.LabCourse', null=True),
        ),
        migrations.AddField(
            model_name='coursemap',
            name='foss',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AlterUniqueTogether(
            name='trainingplanner',
            unique_together=set([('year', 'academic', 'organiser', 'semester')]),
        ),
        migrations.AlterUniqueTogether(
            name='trainingattend',
            unique_together=set([('training', 'student')]),
        ),
        migrations.AlterUniqueTogether(
            name='studentmaster',
            unique_together=set([('batch', 'student')]),
        ),
        migrations.AlterUniqueTogether(
            name='studentbatch',
            unique_together=set([('academic', 'year', 'department')]),
        ),
        migrations.AlterUniqueTogether(
            name='singletrainingattendance',
            unique_together=set([('training', 'firstname', 'lastname', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='singletraining',
            unique_together=set([('organiser', 'academic', 'course', 'tdate', 'ttime')]),
        ),
        migrations.AlterUniqueTogether(
            name='coursemap',
            unique_together=set([('course', 'foss', 'category')]),
        ),
    ]
