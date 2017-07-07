# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0007_auto_20170403_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fosscategory',
            name='category',
            field=models.ManyToManyField(to='creation.FossSuperCategory'),
        ),
    ]
