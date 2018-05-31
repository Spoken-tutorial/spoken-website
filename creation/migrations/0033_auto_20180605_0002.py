# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0032_auto_20180605_0001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentchallan',
            old_name='challan_code',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='paymentchallan',
            old_name='challan_doc',
            new_name='doc',
        ),
        migrations.RenameField(
            model_name='paymentchallan',
            old_name='challan_status',
            new_name='status',
        ),
    ]
