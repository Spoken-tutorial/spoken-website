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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('fname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('roll_no', models.CharField(max_length=50)),
                ('created', models.DateTimeField(null=True, auto_now_add=True)),
                ('updated', models.DateTimeField(null=True, auto_now=True)),
                ('foss', models.ForeignKey(null=True, to='creation.FossCategory')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='learner',
            unique_together=set([('email',)]),
        ),
    ]
