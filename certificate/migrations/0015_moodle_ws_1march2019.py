# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0014_koha_ws_8feb2019'),
    ]

    operations = [
        migrations.CreateModel(
            name='Moodle_WS_1march2019',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('college', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'MCW', max_length=10)),
            ],
        ),
    ]
