# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0031_tutorialpayment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentchallan',
            name='challan_doc',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
    ]
