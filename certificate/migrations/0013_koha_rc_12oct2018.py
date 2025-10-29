# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0012_koha_ws_12oct2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Koha_RC_12oct2018',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('rcid', models.CharField(max_length=500)),
                ('remote', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'KRC', max_length=10)),
            ],
        ),
    ]
