# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0006_auto_20170329_1132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fosscategory',
            options={'ordering': ('foss',), 'verbose_name': 'FOSS', 'verbose_name_plural': 'FOSSes'},
        ),
        migrations.AlterModelOptions(
            name='fosssupercategory',
            options={'ordering': ('name',), 'verbose_name': 'FOSS Category', 'verbose_name_plural': 'FOSS Categories'},
        ),
        
    ]
