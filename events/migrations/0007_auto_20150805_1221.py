# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20150805_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentstream',
            name='student_stream',
            field=models.CharField(max_length=50, choices=[(b'0', b'Engineering'), (b'1', b'science'), (b'2', b'Arts and Humanities'), (b'3', b'Polytechnic/ Diploma programs'), (b'4', b'Commerce and Business Studies'), (b'5', b'Schools'), (b'6', b'ITI'), (b'7', b'Other (need to give textbox)')]),
        ),
    ]
