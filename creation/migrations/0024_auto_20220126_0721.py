# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2022-01-26 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0023_auto_20220114_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankdetail',
            name='vendor',
            field=models.CharField(default=0, max_length=11),
        ),
        migrations.AddField(
            model_name='bankdetail',
            name='vendoraddress',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
