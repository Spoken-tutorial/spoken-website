# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0037_auto_20190306_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingrequest',
            name='cert_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
