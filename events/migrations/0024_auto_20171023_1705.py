# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0023_auto_20171023_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='inductioninterest',
            name='other_language',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='medium_of_studies',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'Assamese', b'Assamese'), (b'Bengali', b'Bengali'), (b'Bhojpuri', b'Bhojpuri'), (b'Bodo', b'Bodo'), (b'English', b'English'), (b'Gujarati', b'Gujarati'), (b'Hindi', b'Hindi'), (b'Kannada', b'Kannada'), (b'Kashmiri', b'Kashmiri'), (b'Khasi', b'Khasi'), (b'Konkani', b'Konkani'), (b'Maithili', b'Maithili'), (b'Malayalam', b'Malayalam'), (b'Manipuri', b'Manipuri'), (b'Marathi', b'Marathi'), (b'Nepali', b'Nepali'), (b'Oriya', b'Oriya'), (b'Punjabi', b'Punjabi'), (b'Rajasthani', b'Rajasthani'), (b'Sanskrit', b'Sanskrit'), (b'Santhali', b'Santhali'), (b'Sindhi', b'Sindhi'), (b'Tamil', b'Tamil'), (b'Telugu', b'Telugu'), (b'Urdu', b'Urdu'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='mother_tongue',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'Assamese', b'Assamese'), (b'Bengali', b'Bengali'), (b'Bhojpuri', b'Bhojpuri'), (b'Bodo', b'Bodo'), (b'English', b'English'), (b'Gujarati', b'Gujarati'), (b'Hindi', b'Hindi'), (b'Kannada', b'Kannada'), (b'Kashmiri', b'Kashmiri'), (b'Khasi', b'Khasi'), (b'Konkani', b'Konkani'), (b'Maithili', b'Maithili'), (b'Malayalam', b'Malayalam'), (b'Manipuri', b'Manipuri'), (b'Marathi', b'Marathi'), (b'Nepali', b'Nepali'), (b'Oriya', b'Oriya'), (b'Punjabi', b'Punjabi'), (b'Rajasthani', b'Rajasthani'), (b'Sanskrit', b'Sanskrit'), (b'Santhali', b'Santhali'), (b'Sindhi', b'Sindhi'), (b'Tamil', b'Tamil'), (b'Telugu', b'Telugu'), (b'Urdu', b'Urdu'), (b'Other', b'Other')]),
        ),
    ]
