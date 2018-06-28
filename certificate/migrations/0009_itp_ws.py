# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0008_auto_20170809_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='ITP_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('college', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'ITP', max_length=10)),
            ],
        ),
    ]
