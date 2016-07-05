# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Learner',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('fname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('roll_no', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('foss', models.ForeignKey(null=True, to='creation.FossCategory')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='learner',
            unique_together=set([('email',)]),
        ),
    ]
