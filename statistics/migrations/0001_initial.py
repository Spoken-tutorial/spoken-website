# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Learner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('roll_no', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='learner',
            unique_together=set([('email',)]),
        ),
    ]
