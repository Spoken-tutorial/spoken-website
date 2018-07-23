# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_paymenttransactiondetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentdetails',
            name='academic_year',
            field=models.PositiveIntegerField(default=2018),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='paymentdetails',
            unique_together=set([('academic_id', 'academic_year')]),
        ),
    ]
