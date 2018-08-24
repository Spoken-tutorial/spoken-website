# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0029_mumbaistudents'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accountexecutive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('academic', models.ForeignKey(blank=True, to='events.AcademicCenter', null=True)),
                ('appoved_by', models.ForeignKey(related_name='accountexecutive_approved_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(related_name='accountexecutive', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
