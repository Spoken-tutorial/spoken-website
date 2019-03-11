# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0013_koha_rc_12oct2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Koha_WS_8feb2019',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('college', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'KCW', max_length=10)),
            ],
        ),
    ]
