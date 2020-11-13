# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-13 06:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donate', '0004_auto_20201111_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationtransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='goodiestransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
