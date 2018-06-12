# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0007_auto_20170403_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='fosscategory',
            name='is_learners_allowed',
            field=models.BooleanField(default=0, max_length=2),
        ),
        migrations.AlterField(
            model_name='fosscategory',
            name='category',
            field=models.ManyToManyField(to='creation.FossSuperCategory'),
        ),
    ]
