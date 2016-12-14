# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_learndrupalfeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingrequest',
            name='course_type',
            field=models.PositiveIntegerField(default=None),
        ),
    ]
