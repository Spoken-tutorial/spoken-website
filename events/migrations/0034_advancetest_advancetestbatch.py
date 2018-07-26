# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaksh', '0014_auto_20180620_1004'),
        ('creation', '0012_tutorialresource_publish_at'),
        ('events', '0033_auto_20180724_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvanceTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('qualifying_marks', models.DecimalField(default=90, max_digits=5, decimal_places=2)),
                ('foss', models.OneToOneField(related_name='advance_test_foss', to='creation.FossCategory')),
                ('yaksh_course', models.OneToOneField(to='yaksh.Course')),
            ],
        ),
        migrations.CreateModel(
            name='AdvanceTestBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(null=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Requested'), (2, b'Invigilator Approved'), (3, b'Resoure Person Approved'), (4, b'Invigilated'), (5, b'Completed'), (20, b'Invigilator Rejected'), (30, b'ResourcePerson Rejected')])),
                ('is_open', models.BooleanField(default=True)),
                ('appeared', models.ManyToManyField(related_name='advance_appeared', to='events.Student')),
                ('approved_by', models.ForeignKey(related_name='advance_test_approved_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('attendees', models.ManyToManyField(related_name='advance_attendees', to='events.Student')),
                ('invigilator', models.ForeignKey(related_name='advance_test_invigilator', to='events.Invigilator', null=True)),
                ('organiser', models.ForeignKey(related_name='advance_test_organiser', to='events.Organiser')),
                ('preliminary_test', models.ForeignKey(related_name='pretest', to='events.Test')),
                ('students', models.ManyToManyField(related_name='advance_students', to='events.Student')),
                ('test', models.ForeignKey(related_name='advance_test', to='events.AdvanceTest')),
            ],
        ),
    ]
