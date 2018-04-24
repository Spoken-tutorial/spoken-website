# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_auto_20180420_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancetestbatch',
            name='appeared',
            field=models.ManyToManyField(related_name='advance_appeared', to='events.Student'),
        ),
        migrations.AlterField(
            model_name='advancetestbatch',
            name='attendees',
            field=models.ManyToManyField(related_name='advance_attendees', to='events.Student'),
        ),
        migrations.AlterField(
            model_name='advancetestbatch',
            name='students',
            field=models.ManyToManyField(related_name='advance_students', to='events.Student'),
        ),
    ]
