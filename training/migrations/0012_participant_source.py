# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2024-07-02 22:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_auto_20230127_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='source',
            field=models.CharField(default=None, max_length=25, null=True),
        ),
    ]
