# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_auto_20180412_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancetestbatch',
            name='appeared',
            field=models.ManyToManyField(related_name='advance_appeared', null=True, to='events.Student'),
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='attendees',
            field=models.ManyToManyField(related_name='advance_attendees', null=True, to='events.Student'),
        ),
        migrations.AlterField(
            model_name='advancetestbatch',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Requested'), (2, b'Resoure Person Approved'), (3, b'Invigilator Approved'), (4, b'Invigilated'), (5, b'Completed'), (20, b'Resoure Person Rejected'), (30, b'Invigilator Rejected')]),
        ),
    ]
