# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0029_advancetestbatch_preliminary_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advancetestbatch',
            name='batch',
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='approved_by',
            field=models.ForeignKey(related_name='advance_test_approved_by', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='invigilator',
            field=models.ForeignKey(related_name='advance_test_invigilator', to='events.Invigilator', null=True),
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='organiser',
            field=models.ForeignKey(related_name='advance_test_organiser', default=None, to='events.Organiser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advancetestbatch',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Requested'), (2, b'Approved'), (3, b'Invigilated'), (4, b'Inprogress'), (5, b'Completed')]),
        ),
        migrations.AlterField(
            model_name='advancetest',
            name='foss',
            field=models.OneToOneField(related_name='advance_test_foss', to='creation.FossCategory'),
        ),
    ]
