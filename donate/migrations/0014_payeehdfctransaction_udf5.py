# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2025-03-26 06:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donate', '0013_auto_20250324_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='payeehdfctransaction',
            name='udf5',
            field=models.CharField(default='-', max_length=255),
            preserve_default=False,
        ),
    ]
