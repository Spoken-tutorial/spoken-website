# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2023-02-15 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0023_fosscategory_credits'),
    ]

    operations = [
        migrations.AddField(
            model_name='fosscategory',
            name='is_fossee',
            field=models.BooleanField(default=False, verbose_name='Added by FOSSEE'),
        ),
    ]
